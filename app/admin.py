# admin.py
from django.contrib import admin
from .models import AppConfigModel

@admin.register(AppConfigModel)
class AppConfigModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'path', 'is_active', 'environment', 'created_at')
    list_filter = ('is_active', 'environment', 'created_at')
    search_fields = ('name', 'host', 'path')
    readonly_fields = ('created_at', 'updated_at')