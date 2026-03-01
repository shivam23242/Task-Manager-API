from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..service import user_service

UNAUTHORIZED_RESPONSE = {'detail': 'Authentication credentials were not provided.'}


@api_view(['POST'])
def register_view(request):
    user, tokens, error_code = user_service.register_user(request.data)
    if error_code:
        return Response({'error': 'Could not create session right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'user': user_service.serialize_user(user),
        'tokens': tokens,
        'message': 'User registered successfully',
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_view(request):
    user, tokens, error_code = user_service.login_user(request.data)
    if error_code == "invalid_credentials":
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    if error_code:
        return Response({'error': 'Login failed. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'user': user_service.serialize_user(user),
        'tokens': tokens,
        'message': 'Login successful',
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_view(request):
    if not user_service.is_authenticated_user(request.user):
        return Response(UNAUTHORIZED_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

    error_code = user_service.logout_user(request.auth)
    if error_code == "db_error":
        return Response({'error': 'Could not logout right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH'])
def user_profile_view(request):
    if not user_service.is_authenticated_user(request.user):
        return Response(UNAUTHORIZED_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        return Response(user_service.serialize_user(request.user))

    profile_data = user_service.update_user_profile(
        request.user,
        request.data,
        partial=(request.method == 'PATCH'),
    )
    return Response(profile_data)


@api_view(['POST'])
def change_password_view(request):
    if not user_service.is_authenticated_user(request.user):
        return Response(UNAUTHORIZED_RESPONSE, status=status.HTTP_401_UNAUTHORIZED)

    error_code = user_service.change_password(request.user, request.data)
    if error_code == "old_password_incorrect":
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    if error_code:
        return Response({'error': 'Could not change password right now.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
