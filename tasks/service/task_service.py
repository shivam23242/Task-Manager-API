from ..permissions import IsOwnerOrAdmin
from ..repo import task_repository
from ..serializers import TaskCreateSerializer, TaskSerializer, TaskUpdateSerializer


def is_authenticated_user(user):
    return bool(user and user.is_authenticated)


def get_filtered_tasks(request, user):
    queryset, error_code = task_repository.get_task_queryset_for_user(user)
    if error_code:
        return None, error_code
    return task_repository.apply_task_query_options(request, queryset)


def create_task(user, payload):
    serializer = TaskCreateSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    task = serializer.save(owner=user)
    return task, None


def get_task_for_user(user, pk):
    return task_repository.get_task_or_404_for_user(user, pk)


def can_access_task(request, task):
    permission = IsOwnerOrAdmin()
    return permission.has_object_permission(request, view=None, obj=task)


def update_task(task, payload, partial=False):
    serializer = TaskUpdateSerializer(task, data=payload, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return task, None


def delete_task(task):
    _, error_code = task_repository.delete_task(task)
    return error_code


def serialize_task(task):
    return TaskSerializer(task).data


def serialize_tasks(tasks):
    return TaskSerializer(tasks, many=True).data


def get_task_stats_for_user(user):
    queryset, error_code = task_repository.get_task_queryset_for_user(user)
    if error_code:
        return None, error_code
    return task_repository.get_task_stats(queryset)
