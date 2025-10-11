from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


def healthz(_request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("leads.urls", namespace="leads")),
]