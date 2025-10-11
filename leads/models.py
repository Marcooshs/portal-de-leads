from django.conf import settings
from django.db import models
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'Novo'
        QUALIFIED = 'QLF', 'Qualidade'
        WON = 'WON', 'Ganho'
        LOST = 'LST', 'Perdido'
        COLD = 'CLD', 'Frio'

    class Source(models.TextChoices):
        WEBSITE = 'WEB', 'Website'
        ADS = 'ADS', 'Anúncio'
        REFERRAL = 'REF', 'Indicação'
        EVENT = 'EVT', 'Evento'
        OTHER = 'OTH', 'Outro'

    name = models.CharField('Nome', max_length=120)
    email = models.EmailField('Email', blank=True)
    phone = models.CharField('Telefone', max_length=30, blank=True)
    company = models.CharField('Empresa', max_length=120, blank=True)

    status = models.CharField(max_length=3, choices=Status.choices, default=Status.NEW)
    source = models.CharField(max_length=3, choices=Source.choices, default=Source.OTHER)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads'
    )
    tags = models.ManyToManyField(Tag, blank=True)

    value = models.DecimalField('Valor estimado', max_digits=12, decimal_places=2, default=0)
    notes = models.TextField('Notas', blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'company'], name= 'unique_lead_email_per_company', condition=~models.Q(email='')
            )
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.company})'