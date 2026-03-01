from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from ..serializers import TaskCreateSerializer, TaskSerializer, TaskUpdateSerializer
from ..service import task_service

UNAUTHORIZED_RESPONSE = {'detail': 'Authentication credentials were not provided.'}


@extend_schema(
    tags=['Tasks'],
    parameters=[
        OpenApiParameter(name='completed', type=bool, description='Filter by completion status'),
        OpenApiParameter(name='title', type=str, description='Filter by title (case-insensitive contains)'),
        OpenApiParameter(name='description', type=str, description='Filter by description (case-insensitive contains)'),
        OpenApiParameter(name='created_after', type=str, description='Filter tasks created after this date (ISO format)'),
        OpenApiParameter(name='created_before', type=str, description='Filter tasks created before this date (ISO format)'),
        OpenApiParameter(name='search', type=str, description='Search in title and description'),
        OpenApiParameter(
            name='ordering',
            type=str,
            description='Order by field (prefix with - for descending). Options: created_at, updated_at, title, completed',
        ),
        OpenApiParameter(name='page', type=int, description='Page number for pagination'),
        OpenApiParameter(name='page_size', type=int, description='Number of items per page'),
    ],
    request=TaskCreateSerializer,
    responses={
        200: TaskSerializer(many=True),
        201: TaskSerializer,
        400: OpenApiResponse(description='Bad request'),
    },
)
@api_view(['GET', 'POST'])
def task_list_create_view(request):
    if not task_service.is_authenticated_user(request.user):
        return Response(UNAUTHORIZED_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        task, error_code = task_service.create_task(request.user, request.data)
        if error_code:
            return Response({'error': 'Could not create task right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(task_service.serialize_task(task), status=status.HTTP_201_CREATED)

    queryset, error_code = task_service.get_filtered_tasks(request, request.user)
    if error_code:
        return Response({'error': 'Could not load tasks right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    return paginator.get_paginated_response(task_service.serialize_tasks(page))


@extend_schema(
    tags=['Tasks'],
    request=TaskUpdateSerializer,
    responses={
        200: TaskSerializer,
        204: OpenApiResponse(description='Task deleted successfully'),
        400: OpenApiResponse(description='Bad request'),
        403: OpenApiResponse(description='Permission denied'),
        404: OpenApiResponse(description='Task not found'),
    },
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def task_detail_view(request, pk):
    if not task_service.is_authenticated_user(request.user):
        return Response(UNAUTHORIZED_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

    task, error_code = task_service.get_task_for_user(request.user, pk)
    if error_code:
        return Response({'error': 'Could not load task right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not task_service.can_access_task(request, task):
        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        return Response(task_service.serialize_task(task))

    if request.method in ['PUT', 'PATCH']:
        updated_task, error_code = task_service.update_task(task, request.data, partial=(request.method == 'PATCH'))
        if error_code:
            return Response({'error': 'Could not update task right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(task_service.serialize_task(updated_task))

    error_code = task_service.delete_task(task)
    if error_code:
        return Response({'error': 'Could not delete task right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Tasks'],
    responses={
        200: OpenApiResponse(
            description='Task statistics',
            response={
                'type': 'object',
                'properties': {
                    'total_tasks': {'type': 'integer'},
                    'completed_tasks': {'type': 'integer'},
                    'pending_tasks': {'type': 'integer'},
                },
            },
        ),
    },
)
@api_view(['GET'])
def task_stats_view(request):
    if not task_service.is_authenticated_user(request.user):
        return Response(UNAUTHORIZED_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

    stats, error_code = task_service.get_task_stats_for_user(request.user)
    if error_code:
        return Response({'error': 'Could not load task stats right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(stats)
