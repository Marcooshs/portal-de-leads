from pathlib import Path
import os

# -------- .env ----------
try:
    from dotenv import load_dotenv
    load_dotenv()

except Exception:
    pass

# -------- Paths ---------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------- Segurança -----
def _env_bool(name: str, default: str = "False") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "t", "yes", "y", "on"}

DEBUG = _env_bool("DEBUG", "True")

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "o4&=c4l#&i5glz)pwkvvl@59g5q1nuk1jw=$+77nq4-%(&#rz&"
    else:
        raise RuntimeError("SECRET_KEY environment variable must be set when DEBUG is False")

def _csv_env(name: str, default: str = "") -> list[str]:
    return [i.strip() for i in os.getenv(name, default).split(",") if i.strip()]

ALLOWED_HOSTS = _csv_env("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = _csv_env("CSRF_TRUSTED_ORIGINS", "")

# -------- Apps ----------
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "leads",
    "widget_tweaks",
]

# -------- Middleware ----
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------- URLs / ASGI / WSGI ----
ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"

# -------- Templates -----
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------- Databases -----
USE_SQLITE = _env_bool("USE_SQLITE", "True")

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PG_NAME", "portal_leads"),
            "USER": os.getenv("PG_USER", "portal_leads"),
            "PASSWORD": os.getenv("PG_PASSWORD", ""),
            "HOST": os.getenv("PG_HOST", "localhost"),
            "PORT": os.getenv("PG_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }
    }
# -------- Passwords -----
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------- I18N / TZ -----
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "pt-br")
TIME_ZONE = os.getenv("TIME_ZONE", "America/Sao_Paulo")
USE_I18N = True
USE_TZ = True

# -------- Estáticos/Mídia -----
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
WHITENOISE_MAX_AGE = int(os.getenv("WHITENOISE_MAX_AGE", "31536000"))
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = DEBUG

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------- Email (SMTP real) -----
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", "True")
EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", "False")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# -------- Provedores SMTP (para mailers.py) -----
DEFAULT_SMTP_PROVIDER = os.getenv("DEFAULT_SMTP_PROVIDER", "gmail")
SMTP_PROVIDERS = {
    "gmail": {
        "HOST": os.getenv("EMAIL_HOST", "smtp.gmail.com"),
        "PORT": int(os.getenv("EMAIL_PORT", "587")),
        "USER": os.getenv("EMAIL_HOST_USER", ""),
        "PASSWORD": os.getenv("EMAIL_HOST_PASSWORD", ""),
        "USE_TLS": _env_bool("EMAIL_USE_TLS", "True"),
        "USE_SSL": _env_bool("EMAIL_USE_SSL", "False"),
        "DEFAULT_FROM_EMAIL": os.getenv("DEFAULT_FROM_EMAIL", ""),
    },
    "o365": {
        "HOST": os.getenv("O365_HOST", "smtp.office365.com"),
        "PORT": int(os.getenv("O365_PORT", "587")),
        "USER": os.getenv("O365_USER", ""),
        "PASSWORD": os.getenv("O365_PASSWORD", ""),
        "USE_TLS": _env_bool("O365_USE_TLS", "True"),
        "USE_SSL": _env_bool("O365_USE_SSL", "False"),
        "DEFAULT_FROM_EMAIL": os.getenv("O365_FROM_EMAIL", ""),
    },
}

# -------- Auth redirects -----
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "leads:list"
LOGOUT_REDIRECT_URL = "login"

# -------- Segurança extra (produção/HTTPS) -----
SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


# -------- PK default --------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"