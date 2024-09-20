from http.client import HTTPException
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.views import PasswordResetView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordContextMixin
from django.views.generic.edit import FormView
from django.views.decorators.debug import sensitive_post_parameters

from accounts.connectors import LinkedInConnector
from accounts.tasks import send_email_celery_task
from accounts.models import User
from config.logging import log
from .forms import (
    EditUserForm,
    UserAuthForm,
    UserRegistrationForm,
    CustomPasswordChangeForm,
)


@login_required
def personal_information_view(request):
    """
    View to display the personal information of the logged-in user.
    """
    user = request.user
    log("info", f"User {user.email} accessed personal information view")
    context = {
        "user": user,
        "menu": "personal_information",
        "has_usable_password": user.has_usable_password(),
    }
    return render(request, "accounts/personal_information.html", context)


@login_required
def personal_information_edit_view(request):
    """
    View to edit the personal information of the logged-in user.
    """
    user = request.user
    if request.method == "POST":
        form = EditUserForm(instance=user, data=request.POST, files=request.FILES)
        if form.is_valid():
            if form.initial.get("email") != user.email:
                user.is_verified = False
                send_email_celery_task.delay(user.id)
                messages.info(
                    request,
                    "Email verification link has been sent to your email address.",
                )
                log("info", f"User {user.email} changed email, verification link sent")

            form.save()
            messages.success(request, "Your personal information has been updated.")
            log("info", f"User {user.email} updated personal information")
            return redirect(reverse("personal_information"))
    else:
        form = EditUserForm(instance=user)
    context = {
        "form": form,
        "menu": "personal_information",
    }
    return render(request, "accounts/edit_personal_information.html", context)


def login_view(request):
    """
    View to handle user login and registration.
    """
    redirect_to = request.POST.get("next", request.GET.get("next", ""))

    if request.user.is_authenticated:
        if redirect_to == request.path:
            raise ValueError("Redirection loop for authenticated user detected.")
        return redirect(reverse("index"))

    if request.method == "POST":
        form_login = UserAuthForm(request, data=request.POST)
        form_registration = UserRegistrationForm()

        if form_login.is_valid():
            login(request, form_login.get_user())
            log("info", f"User {request.user.email} logged in")
            return redirect(reverse("index"))

    else:
        form_login = UserAuthForm(request)
        form_registration = UserRegistrationForm()

    context = {
        "form_login": form_login,
        "form_registration": form_registration,
    }
    return render(request, "accounts/auth.html", context)


def register_view(request):
    """
    View to handle user registration.
    """
    if request.user.is_authenticated:
        return redirect(reverse("index"))

    if request.method == "POST":
        form_registration = UserRegistrationForm(request.POST)

        if form_registration.is_valid():
            user = form_registration.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            send_email_celery_task.delay(user.id)
            messages.info(
                request, "Email verification link has been sent to your email address."
            )
            log("info", f"User {user.email} registered and logged in")
            return redirect(reverse("index"))
        else:
            context = {
                "form_login": UserAuthForm(),
                "form_registration": form_registration,
            }
            return render(request, "accounts/auth.html", context)

    return redirect(reverse("login"))


def logout_view(request):
    """
    View to handle user logout.
    """
    _next = request.GET.get("next")
    log("info", f"User {request.user.email} logged out")
    logout(request)
    return redirect(_next if _next else settings.LOGOUT_REDIRECT_URL)


def verify_email(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    user = get_object_or_404(User, pk=uid)

    if default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        log("info", f"User {user.email} verified email")
        return HttpResponse("Email successfully verified!")
    else:
        log("warning", f"Invalid verification link for user {user.email}")
        return HttpResponse("Invalid verification link.")


def linkedin_login(request):
    return LinkedInConnector.login_to_provider()


def linkedin_login_callback(request):
    if request.method == "GET":
        try:
            LinkedInConnector.login(request)
            log("info", f"User {request.user.email} logged in via LinkedIn")
            return redirect(reverse("index"))
        except HTTPException as e:
            log("error", f"LinkedIn login error: {e}")
            messages.error(request, "LinkedIn login failed", "error")
            return redirect(reverse("login"))
    return redirect(reverse("login_register"))


class PasswordResetModifiedView(PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    template_name = "registration/password_reset_form.html"
    title = _("Password reset")
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = User.objects.filter(email=form["email"].data).first()
        if user and user.has_usable_password() is False:
            messages.add_message(
                self.request,
                messages.WARNING,
                _("This account cannot reset the password."),
            )
            log(
                "warning",
                f"User {user.email} attempted password reset but has unusable password",
            )
            return redirect("login")

        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        log("info", f'Password reset email sent to {form["email"].data}')
        return super().form_valid(form)


class PasswordCreateView(PasswordContextMixin, FormView):
    form_class = CustomPasswordChangeForm  # Use the custom form
    success_url = reverse_lazy("index")
    template_name = "accounts/password_change_form.html"
    title = _("Password change")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(
            self.request, _("Your password has been successfully changed.")
        )
        log("info", f"User {self.request.user.email} changed password successfully")
        return super().form_valid(form)
