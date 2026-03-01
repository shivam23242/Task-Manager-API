from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'completed', 'created_at', 'updated_at')
    list_filter = ('completed', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'completed', 'owner')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

