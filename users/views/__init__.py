from . import auth_views

change_password_view = auth_views.change_password_view
login_view = auth_views.login_view
logout_view = auth_views.logout_view
register_view = auth_views.register_view
user_profile_view = auth_views.user_profile_view

__all__ = [
    "change_password_view",
    "login_view",
    "logout_view",
    "register_view",
    "user_profile_view",
]
