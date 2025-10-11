from django.urls import path
from .views import (
    LeadListView,
    LeadCreateView,
    LeadUpdateView,
    LeadDeleteView,
    import_csv_view,
)

app_name = "leads"

urlpatterns = [
    path("", LeadListView.as_view(), name="list"),
    path("novo/", LeadCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", LeadUpdateView.as_view(), name="update"),
    path("<int:pk>/remover/", LeadDeleteView.as_view(), name="delete"),
    path("importar/", import_csv_view, name="import"),
]