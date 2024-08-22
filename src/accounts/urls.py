from django.urls import path, re_path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change_form.html",
        ),
        name="password_change",
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            html_email_template_name="accounts/email/password_reset.html",
            subject_template_name="accounts/email/password_reset_subject.txt",
            template_name="accounts/password_reset.html",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<str:uidb64>/<str:token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path(
        "profile/personal-information/",
        views.personal_information_view,
        name="personal_information",
    ),
    path(
        "profile/personal-information/edit/",
        views.personal_information_edit_view,
        name="edit_personal_information",
    ),
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
]
