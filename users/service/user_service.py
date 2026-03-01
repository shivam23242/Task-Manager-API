from ..repo import user_repository
from ..serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


def is_authenticated_user(user):
    return bool(user and user.is_authenticated)


def register_user(payload):
    serializer = RegisterSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    session, error_code = user_repository.create_session(user)
    if error_code:
        return None, None, error_code
    return user, user_repository.build_tokens(user, session), None


def login_user(payload):
    serializer = LoginSerializer(data=payload)
    serializer.is_valid(raise_exception=True)

    user, error_code = user_repository.authenticate_user(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password'],
    )
    if error_code:
        return None, None, error_code

    if user is None:
        return None, None, "invalid_credentials"

    session, error_code = user_repository.create_session(user)
    if error_code:
        return None, None, error_code
    return user, user_repository.build_tokens(user, session), None


def logout_user(validated_token):
    session_id = user_repository.get_session_id_from_token(validated_token)
    if not session_id:
        return "session_missing"

    expired, error_code = user_repository.expire_session_by_id(session_id)
    if error_code:
        return error_code
    if not expired:
        return "session_not_found"
    return None


def serialize_user(user):
    return UserSerializer(user).data


def update_user_profile(user, payload, partial=False):
    serializer = UserSerializer(user, data=payload, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def change_password(user, payload):
    serializer = ChangePasswordSerializer(data=payload)
    serializer.is_valid(raise_exception=True)

    if not user_repository.check_password(user, serializer.validated_data['old_password']):
        return "old_password_incorrect"

    changed, error_code = user_repository.set_password(user, serializer.validated_data['new_password'])
    if error_code or not changed:
        return "db_error"
    return None
