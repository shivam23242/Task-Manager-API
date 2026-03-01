from django.db import DatabaseError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters

from ..filters import TaskFilter
from ..models import Task


class _TaskListBackendView:
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title', 'completed']
    ordering = ['-created_at']


def get_task_queryset_for_user(user):
    try:
        if user.is_admin():
            return Task.objects.all(), None
        return Task.objects.filter(owner=user), None
    except DatabaseError:
        return None, "db_error"


def apply_task_query_options(request, queryset):
    try:
        task_filter = TaskFilter(request.query_params, queryset=queryset)
        if task_filter.is_valid():
            queryset = task_filter.qs

        search_backend = filters.SearchFilter()
        ordering_backend = filters.OrderingFilter()
        queryset = search_backend.filter_queryset(request, queryset, view=_TaskListBackendView())
        return ordering_backend.filter_queryset(request, queryset, view=_TaskListBackendView()), None
    except DatabaseError:
        return None, "db_error"


def get_task_or_404_for_user(user, pk):
    queryset, error_code = get_task_queryset_for_user(user)
    if error_code:
        return None, error_code
    try:
        return get_object_or_404(queryset, pk=pk), None
    except DatabaseError:
        return None, "db_error"


def get_task_stats(queryset):
    try:
        return queryset.aggregate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(completed=True)),
            pending_tasks=Count('id', filter=Q(completed=False)),
        ), None
    except DatabaseError:
        return None, "db_error"


def delete_task(task):
    try:
        task.delete()
        return True, None
    except DatabaseError:
        return False, "db_error"
