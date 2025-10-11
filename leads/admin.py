from django.contrib import admin
from .models import Lead, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name',)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'status', 'source', 'owner', 'created_at')
    list_filter = ('status', 'source', 'owner', 'tags', 'created_at')
    search_fields = ('name', 'email', 'company', 'phone', 'notes')
    autocomplete_fields = ('owner', 'tags')
    date_hierarchy = 'created_at'