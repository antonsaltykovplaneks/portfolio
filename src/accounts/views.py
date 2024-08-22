from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from django.utils.http import urlsafe_base64_decode

from accounts.tasks import send_email_celery_task

from .forms import EditUserForm, UserAuthForm, UserRegistrationForm



@login_required
def personal_information_view(request):
    """
    View to display the personal information of the logged-in user.
    """
    user = request.user
    context = {
        "user": user,
        "menu": "personal_information",
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
            form.save()
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
        form_login = UserAuthForm(request)

        if form_registration.is_valid():
            user = form_registration.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            send_email_celery_task.delay(user.id)
            return redirect(reverse("index"))

    return redirect(reverse("login"))


def logout_view(request):
    """
    View to handle user logout.
    """
    _next = request.GET.get("next")
    logout(request)
    return redirect(_next if _next else settings.LOGOUT_REDIRECT_URL)


def verify_email(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    user = get_object_or_404(User, pk=uid)

    if default_token_generator.check_token(user, token):
        user.profile.email_verified = True
        user.profile.save()
        return HttpResponse("Email successfully verified!")
    else:
        return HttpResponse("Invalid verification link.")
