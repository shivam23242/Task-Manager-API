from . import task_views

task_detail_view = task_views.task_detail_view
task_list_create_view = task_views.task_list_create_view
task_stats_view = task_views.task_stats_view

__all__ = ["task_detail_view", "task_list_create_view", "task_stats_view"]
