import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def get_default_session_expiry():
    session_days = getattr(settings, 'USER_SESSION_DAYS', 7)
    return timezone.now() + timedelta(days=session_days)


class User(AbstractUser):
    """
    Custom User model with role-based permissions
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'Regular User'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role determines permissions'
    )
    email = models.EmailField(unique=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin' or self.is_superuser


class UserSession(models.Model):
    """
    Store login sessions so logout can expire a specific JWT session.
    """
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_default_session_expiry)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.session_id}"
