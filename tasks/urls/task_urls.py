from django.urls import path

from .. import views

urlpatterns = [
    path('tasks', views.task_list_create_view, name='task-list-create'),
    path('tasks/<int:pk>', views.task_detail_view, name='task-detail'),
    path('tasks/stats', views.task_stats_view, name='task-stats'),
]
