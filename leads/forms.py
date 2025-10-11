from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'company', 'status', 'source', 'owner', 'tags', 'value', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.SelectMultiple(attrs={'size': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # Select/SelectMultiple usam 'form-select'; o resto usa 'form-control'
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')

class CSVImportForm(forms.Form):
    file = forms.FileField(
        help_text='CSV com colunas: name,email,phone,company,status,source,value,notes,tags'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.setdefault('class', 'form-control')