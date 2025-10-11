from typing import Iterable, Optional
from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string


def _conn_for(provider: Optional[str] = None):
    """
    Retorna (conexao_smtp, config) para o provedor indicado.
    provider: "gmail" | "o365" | None (usa DEFAULT_SMTP_PROVIDER)
    """
    name = (provider or settings.DEFAULT_SMTP_PROVIDER).lower()
    conf = settings.SMTP_PROVIDERS.get(name)
    if not conf:
        raise ValueError(f"SMTP provider '{name}' não configurado.")

    conn = get_connection(
        backend=settings.EMAIL_BACKEND,
        host=conf['HOST'],
        port=conf['PORT'],
        username=conf['USER'],
        password=conf['PASSWORD'],
        use_tls=conf['USE_TLS'],
        use_ssl=conf['USE_SSL'],
        timeout=15,
    )
    return conn, conf


def send_mail_using(
    provider: Optional[str],
    subject: str,
    text_body: str,
    to: Iterable[str],
    from_email: Optional[str] = None,
    html_body: Optional[str] = None,
    cc: Optional[Iterable[str]] = None,
    bcc: Optional[Iterable[str]] = None,
    reply_to: Optional[Iterable[str]] = None,
) -> int:
    """
    Envia e-mail via provedor escolhido: "gmail" ou "o365".
    Retorna a quantidade de mensagens enviadas (0 ou 1).
    """
    conn, conf = _conn_for(provider)
    sender = from_email or conf['DEFAULT_FROM_EMAIL'] or conf['USER']
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=sender,
        to=list(to),
        cc=list(cc or []),
        bcc=list(bcc or []),
        reply_to=list(reply_to or []),
        connection=conn,
    )
    if html_body:
        msg.attach_alternative(html_body, 'text/html')
    return msg.send()


def send_templated_mail(
    provider: Optional[str],
    subject: str,
    template_base: str,
    context: dict,
    to: Iterable[str],
    from_email: Optional[str] = None,
    cc: Optional[Iterable[str]] = None,
    bcc: Optional[Iterable[str]] = None,
    reply_to: Optional[Iterable[str]] = None,
) -> int:
    """
    Envia e-mail usando templates:
      - leads/templates/email/<template_base>.txt
      - leads/templates/email/<template_base>.html
    """
    conn, conf = _conn_for(provider)
    sender = from_email or conf['DEFAULT_FROM_EMAIL'] or conf['USER']

    text_body = render_to_string(f'email/{template_base}.txt', context)
    html_body = render_to_string(f'email/{template_base}.html', context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=sender,
        to=list(to),
        cc=list(cc or []),
        bcc=list(bcc or []),
        reply_to=list(reply_to or []),
        connection=conn,
    )
    if html_body:
        msg.attach_alternative(html_body, 'text/html')
    return msg.send()