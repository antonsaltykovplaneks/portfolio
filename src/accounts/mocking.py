import datetime
import json
import random
from typing import List

from django.core import serializers
from faker import Faker

from accounts.models import User

fake = Faker()

DEFAULT_USER_COUNT = 10


class UserFactory:

    @staticmethod
    def create(
        email: str = None,
        name: str = None,
        password: str = None,
        is_linkedin_user: bool = None,
        is_verified: bool = None,
        is_active: bool = None,
        date_joined: datetime.datetime = None,
        last_login: datetime.datetime = None,
    ) -> User:
        """Create a user object. Uses Faker to generate random data if not provided.

        Args:
            email (str, optional). Defaults to None.
            name (str, optional). Defaults to None.
            password (str, optional). Defaults to None.
            is_linkedin_user (bool, optional). Defaults to None.
            is_verified (bool, optional). Defaults to None.
            is_active (bool, optional). Defaults to None.
            date_joined (datetime.datetime, optional). Defaults to None.
            last_login (datetime.datetime, optional). Defaults to None.

        Returns:
            User: user object
        """
        object_fields = {}
        object_fields["email"] = email or fake.email()
        object_fields["name"] = name or fake.name()
        object_fields["password"] = password or fake.password()
        object_fields["is_linkedin_user"] = (
            is_linkedin_user
            if is_linkedin_user is not None
            else random.choice([True, False])
        )
        object_fields["is_verified"] = (
            is_verified if is_verified is not None else random.choice([True, False])
        )
        is_active = is_active if is_active is not None else random.choice([True, False])
        date_joined = date_joined or fake.date_time_this_year()
        last_login = last_login or fake.date_time_this_year()

        user = User.objects.create_user(**object_fields)
        user.is_active = is_active
        user.date_joined = date_joined
        user.last_login = last_login
        user.save()

        return user

    @staticmethod
    def create_many(count: int = DEFAULT_USER_COUNT) -> List[User]:
        """Create a list of user objects

        Args:
            count (int, optional): number of Users to create. Defaults to DEFAULT_USER_COUNT.

        Returns:
            List[User]: list of User objects
        """
        users = []
        for _ in range(count):
            user = UserFactory.create()
            users.append(user)
        return users

    @staticmethod
    def export(count: int = DEFAULT_USER_COUNT) -> None:
        """Create a list of user objects and save them to a JSON file

        Args:
            count (int, optional): Number of Users to create. Defaults to DEFAULT_USER_COUNT.
        """
        users = User.objects.all()
        if not users:
            users = UserFactory.create_many(count)

        users_json = serializers.serialize("json", users)

        with open("accounts/fixtures/users.json", "w+") as file:
            json.dump(users_json, file, indent=4)

    @staticmethod
    def import_json(file_path: str = "accounts/fixtures/users.json") -> None:
        """Import users from a JSON file

        Args:
            file_path (str): Path to JSON file
        """
        with open(file_path, "r") as file:
            users_json = json.loads(file.read())
        for user_json in users_json:
            is_active = user_json["fields"].pop("is_active")
            date_joined = user_json["fields"].pop("date_joined")
            last_login = user_json["fields"].pop("last_login")
            is_superuser = user_json["fields"].pop("is_superuser")
            is_staff = user_json["fields"].pop("is_staff")
            groups = user_json["fields"].pop("groups")
            user_permissions = user_json["fields"].pop("user_permissions")

            user = User.objects.create_user(**user_json["fields"])

            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.is_active = is_active
            user.date_joined = date_joined
            user.last_login = last_login
            user.groups.set(groups)
            user.user_permissions.set(user_permissions)
            user.save()
