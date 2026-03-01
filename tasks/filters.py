import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    """
    Filter class for Task model with advanced filtering options
    """
    title = django_filters.CharFilter(lookup_expr='icontains', help_text='Filter by title (case-insensitive)')
    description = django_filters.CharFilter(lookup_expr='icontains', help_text='Filter by description (case-insensitive)')
    completed = django_filters.BooleanFilter(help_text='Filter by completion status')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte', help_text='Filter tasks created after this date')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte', help_text='Filter tasks created before this date')
    
    class Meta:
        model = Task
        fields = ['completed', 'title', 'description']

