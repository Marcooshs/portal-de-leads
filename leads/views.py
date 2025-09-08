import csv
import io
from decimal import Decimal
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import LeadForm, CSVImportForm
from .models import Lead, Tag
from .mailers import send_templated_mail


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    paginate_by = 20

    def _should_export(self) -> bool:
        return self.request.GET.get("format", "").lower() == "csv"

    def get_paginate_by(self, queryset):
        # Exporta tudo quando for CSV (sem paginação)
        return None if self._should_export() else self.paginate_by

    def get_queryset(self):
        qs = Lead.objects.select_related("owner").prefetch_related("tags")
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        source = self.request.GET.get("source", "").strip()
        tag = self.request.GET.get("tag", "").strip()
        owner = self.request.GET.get("owner", "").strip()

        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(email__icontains=q)
                | Q(company__icontains=q)
                | Q(phone__icontains=q)
                | Q(notes__icontains=q)
            )
        if status:
            qs = qs.filter(status=status)
        if source:
            qs = qs.filter(source=source)
        if tag:
            qs = qs.filter(tags__id=tag)
        if owner:
            qs = qs.filter(owner__id=owner)

        return qs.distinct()  # evita duplicados com M2M

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tags"] = Tag.objects.order_by("name")
        ctx["owners"] = get_user_model().objects.order_by("username")
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if not self._should_export():
            return super().render_to_response(context, **response_kwargs)

        qs = context["object_list"]

        class Echo:
            @staticmethod
            def write(value):
                return value

        def row_iter():
            # BOM para Excel (Windows) reconhecer UTF-8
            yield "\ufeff"
            writer = csv.writer(Echo(), lineterminator="\n")
            # Cabeçalho
            yield writer.writerow([
                "name", "email", "phone", "company", "status", "source",
                "owner", "value", "tags", "notes", "created_at",
            ])
            # Linhas
            for lead in qs:
                tags = ", ".join(lead.tags.values_list("name", flat=True))
                owner = lead.owner.get_username() if lead.owner else ""
                yield writer.writerow([
                    lead.name,
                    lead.email,
                    lead.phone,
                    lead.company,
                    lead.get_status_display(),
                    lead.get_source_display(),
                    owner,
                    f"{lead.value:.2f}",
                    tags,
                    (lead.notes or "").replace("\r\n", " ").replace("\n", " "),
                    lead.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ])

        resp = StreamingHttpResponse(row_iter(), content_type="text/csv; charset=utf-8")
        filename = "leads.csv"
        resp["Content-Disposition"] = (
            f'attachment; filename="{filename}"; filename*=UTF-8\'\'{quote(filename)}'
        )
        return resp

class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = "leads/lead_form.html"
    success_url = reverse_lazy("leads:list")

    def form_valid(self, form):
        lead = form.save(commit= False)
        if not lead.owner_id:
            lead.owner = self.request.user
        lead.save()
        form.save_m2m()

        # Escolha do provedor por querystring (?provider=gmail|o365); se não vier, usa o padrão do .env
        provider = (self.request.GET.get('provider') or '').lower() or None
        to = [self.request.user.email] if self.request.user.email else []

        if to:
            try:
                subject = f'Novo Lead: {lead.name}'
                context = {'lead': lead, 'user': self.request.user}
                send_templated_mail(
                    provider= provider,
                    subject= subject,
                    template_base= 'new_lead',
                    context= context,
                    to= to,
                )
            except Exception as exc:
                messages.warning(self.request,f'Lead criado, mas falhou envio de e-mail: {exc}')

        messages.success(self.request,f'Lead criado com sucesso ✔️')
        return super().form_valid(form)

class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = "leads/lead_form.html"
    success_url = reverse_lazy("leads:list")

    def form_valid(self, form):
        messages.success(self.request, "Lead atualizado com sucesso ✔️")
        return super().form_valid(form)

class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    template_name = "leads/lead_confirm_delete.html"
    success_url = reverse_lazy("leads:list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Lead removido ✔️")
        return super().delete(request, *args, **kwargs)

@login_required
def import_csv_view(request):
    if request.method == "POST":
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            decoded = file.read().decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(decoded))
            created = 0
            with transaction.atomic():
                for row in reader:
                    # tags
                    tags_names = [t.strip() for t in (row.get("tags") or "").split(",") if t.strip()]
                    tag_objs = [Tag.objects.get_or_create(name=n)[0] for n in tags_names]

                    # valor
                    value_raw = (row.get("value") or "0").replace(",", ".")
                    try:
                        value = Decimal(value_raw)
                    except Exception:
                        value = Decimal("0")

                    lead = Lead.objects.create(
                        name=(row.get("name") or "").strip(),
                        email=(row.get("email") or "").strip(),
                        phone=(row.get("phone") or "").strip(),
                        company=(row.get("company") or "").strip(),
                        status=(row.get("status") or Lead.Status.NEW),
                        source=(row.get("source") or Lead.Source.OTHER),
                        value=value,
                        notes=(row.get("notes") or "").strip(),
                        owner=request.user if request.user.is_authenticated else None,
                    )
                    if tag_objs:
                        lead.tags.add(*tag_objs)
                    created += 1
            messages.success(request, f"Importação concluída: {created} leads ✔️")
            return redirect("leads:list")
    else:
        form = CSVImportForm()
    return render(request, "leads/import_csv.html", {"form": form})
