from django.contrib.auth import authenticate
from django.db import DatabaseError
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from ..models import UserSession


def authenticate_user(username, password):
    try:
        return authenticate(username=username, password=password), None
    except Exception:
        return None, "auth_error"


def create_session(user):
    try:
        return UserSession.objects.create(user=user), None
    except DatabaseError:
        return None, "db_error"


def get_session_id_from_token(validated_token):
    if not validated_token:
        return None
    session_id = validated_token.get('session_id')
    return str(session_id) if session_id else None


def is_session_active(session_id):
    try:
        is_active = UserSession.objects.filter(
            session_id=session_id,
            is_active=True,
            expires_at__gt=timezone.now(),
        ).exists()
        return is_active, None
    except DatabaseError:
        return False, "db_error"


def expire_session_by_id(session_id):
    try:
        session = UserSession.objects.filter(
            session_id=session_id,
            is_active=True,
        ).first()
        if session is None:
            return False, None

        session.is_active = False
        session.expires_at = timezone.now()
        session.save(update_fields=['is_active', 'expires_at'])
        return True, None
    except DatabaseError:
        return False, "db_error"


def build_tokens(user, session):
    access = AccessToken.for_user(user)
    access['session_id'] = str(session.session_id)
    return {
        'access': str(access),
    }


def check_password(user, raw_password):
    return user.check_password(raw_password)


def set_password(user, raw_password):
    try:
        user.set_password(raw_password)
        user.save()
        return True, None
    except DatabaseError:
        return False, "db_error"
