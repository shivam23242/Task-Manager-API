from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from .repo import user_repository


class SessionJWTAuthentication(JWTAuthentication):
    """
    JWT auth that also validates the token belongs to an active DB session.
    """

    def authenticate(self, request):
        auth_result = super().authenticate(request)
        if auth_result is None:
            custom_token = request.META.get('HTTP_ACCESS_TOKEN')
            if not custom_token:
                return None

            validated_token = self.get_validated_token(custom_token)
            user = self.get_user(validated_token)
        else:
            user, validated_token = auth_result

        session_id = user_repository.get_session_id_from_token(validated_token)
        if not session_id:
            raise AuthenticationFailed("Session is missing. Please login again.")

        is_active, error_code = user_repository.is_session_active(session_id)
        if error_code:
            raise AuthenticationFailed("Could not validate session right now.")
        if not is_active:
            raise AuthenticationFailed("Session has expired. Please login again.")

        return user, validated_token
