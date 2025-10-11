from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.contrib.auth import get_user_model

from .models import Lead, Tag


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LeadPortalTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester", password="pass1234", email="tester@example.com"
        )
        self.client = Client()
        self.client.login(username="tester", password="pass1234")

        self.tag_hot = Tag.objects.create(name="Hot")
        self.lead1 = Lead.objects.create(
            name="Alice",
            email="alice@acme.com",
            phone="1111",
            company="Acme",
            status=Lead.Status.NEW,
            source=Lead.Source.WEBSITE,
            owner=self.user,
            value=1000,
            notes="Primeiro contato",
        )
        self.lead1.tags.add(self.tag_hot)

        self.lead2 = Lead.objects.create(
            name="Bob",
            email="bob@beta.com",
            phone="2222",
            company="Beta",
            status=Lead.Status.QUALIFIED,
            source=Lead.Source.REFERRAL,
            owner=self.user,
            value=2000,
            notes="Indicação",
        )

    def test_requires_login(self):
        c = Client()
        resp = c.get(reverse("leads:list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

    def test_list_loads(self):
        resp = self.client.get(reverse("leads:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Alice")
        self.assertContains(resp, "Bob")

    def test_filters_q_status_source_tag_owner(self):
        # busca por texto
        resp = self.client.get(reverse("leads:list"), {"q": "Acme"})
        self.assertContains(resp, "Alice")
        self.assertNotContains(resp, "Bob")

        # por status
        resp = self.client.get(reverse("leads:list"), {"status": Lead.Status.QUALIFIED})
        self.assertContains(resp, "Bob")
        self.assertNotContains(resp, "Alice")

        # por source
        resp = self.client.get(reverse("leads:list"), {"source": Lead.Source.WEBSITE})
        self.assertContains(resp, "Alice")
        self.assertNotContains(resp, "Bob")

        # por tag
        resp = self.client.get(reverse("leads:list"), {"tag": str(self.tag_hot.id)})
        self.assertContains(resp, "Alice")
        self.assertNotContains(resp, "Bob")

        # por owner
        resp = self.client.get(reverse("leads:list"), {"owner": str(self.user.id)})
        self.assertContains(resp, "Alice")
        self.assertContains(resp, "Bob")

    def test_export_csv_streaming(self):
        url = reverse("leads:list") + "?format=csv"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp["Content-Type"])
        self.assertIn("leads.csv", resp["Content-Disposition"])

        # StreamingHttpResponse => juntar conteúdo
        content = b"".join(resp.streaming_content).decode("utf-8-sig")
        # cabeçalho
        self.assertIn("name,email,phone,company,status,source,owner,value,tags,notes,created_at", content)
        # linhas
        self.assertIn("Alice", content)
        self.assertIn("Bob", content)

    def test_create_sends_email_and_persists(self):
        data = {
            "name": "Carol",
            "email": "carol@corp.com",
            "phone": "3333",
            "company": "Corp",
            "status": Lead.Status.NEW,
            "source": Lead.Source.ADS,
            "owner": self.user.id,
            "tags": [self.tag_hot.id],
            "value": "1234.56",
            "notes": "Lead novo",
        }
        resp = self.client.post(reverse("leads:create"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Lead.objects.filter(name="Carol", company="Corp").exists())
        # e-mail enviado (locmem backend)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Novo Lead: Carol", mail.outbox[0].subject)

    def test_update_and_delete(self):
        lead = self.lead2
        # update
        resp = self.client.post(
            reverse("leads:update", args=[lead.pk]),
            {
                "name": "Bob Jr",
                "email": lead.email,
                "phone": lead.phone,
                "company": lead.company,
                "status": Lead.Status.WON,
                "source": lead.source,
                "owner": self.user.id,
                "tags": [self.tag_hot.id],
                "value": "2500.00",
                "notes": "Atualizado",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        lead.refresh_from_db()
        self.assertEqual(lead.name, "Bob Jr")
        self.assertEqual(lead.status, Lead.Status.WON)

        # delete
        resp = self.client.post(reverse("leads:delete", args=[lead.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Lead.objects.filter(pk=lead.pk).exists())

    def test_import_csv(self):
        csv_content = (
            "name,email,phone,company,status,source,value,notes,tags\n"
            "Diego,diego@ex.com,4444,Delta,NEW,WEB,500,Teste,\"Hot\"\n"
            "Eva,eva@ex.com,5555,Echo,QLF,REF,800,Ok,\"\"\n"
        )
        file = SimpleUploadedFile("leads.csv", csv_content.encode("utf-8"), content_type="text/csv")
        resp = self.client.post(reverse("leads:import"), {"file": file}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Lead.objects.filter(name="Diego", company="Delta").exists())
        self.assertTrue(Lead.objects.filter(name="Eva", company="Echo").exists())