from http.client import HTTPException
from urllib.parse import urlencode

import requests
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse

from accounts.models import User
from config import settings


class LinkedInConnector:
    @classmethod
    def _bad_request_check(cls, response):
        if response.status_code != 200:
            raise HTTPException

    @classmethod
    def login_to_provider(cls):

        params = {
            "response_type": "code",
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": settings.SITE_URL + reverse(settings.LINKEDIN_REDIRECT_URL),
            "state": settings.LINKEDIN_STATE,
            "scope": settings.LINKEDIN_SCOPE,
        }

        return redirect(settings.LINKEDIN_AUTHORIZATION_URL + urlencode(params))

    @classmethod
    def get_authorization_code(self, request):
        return request.GET.get("code")

    @classmethod
    def get_access_token(cls, authorization_code):

        data = {
            "code": authorization_code,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            "redirect_uri": settings.SITE_URL + reverse(settings.LINKEDIN_REDIRECT_URL),
            "grant_type": settings.LINKEDIN_GRANT_TYPE,
        }

        response = requests.post(settings.LINKEDIN_ACCESS_TOKEN_URL, data=data)
        cls._bad_request_check(response)
        return response.json().get("access_token")

    @classmethod
    def get_userinfo(cls, access_token):

        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(settings.LINKEDIN_PROFILE_URL, headers=headers)
        cls._bad_request_check(userinfo_response)
        return userinfo_response.json()

    @classmethod
    def populate_user(cls, userinfo):
        user_email = userinfo.get("email")
        user_name = userinfo.get("name")

        if User.objects.filter(email=user_email).exists():
            linkedin_user = User.objects.filter(email=user_email).first()
        else:
            linkedin_user = User.objects.create(
                email=user_email,
                name=user_name,
                is_linkedin_user=True,
                is_verified=True,
            )
            linkedin_user.set_unusable_password()
            linkedin_user.save()

        return linkedin_user

    @classmethod
    def login(cls, request):
        authorization_code = cls.get_authorization_code(request)
        access_token = cls.get_access_token(authorization_code)
        userinfo = cls.get_userinfo(access_token)

        linkedin_user = cls.populate_user(userinfo=userinfo)
        linkedin_user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, linkedin_user)
        return linkedin_user
