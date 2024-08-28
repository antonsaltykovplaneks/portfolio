import datetime
from typing import List

from faker import Faker

from accounts.models import User

fake = Faker()

DEFAULT_USER_COUNT = 10


def create_user(
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
        is_linkedin_user if is_linkedin_user is not None else fake.boolean()
    )
    object_fields["is_verified"] = (
        is_verified if is_verified is not None else fake.boolean
    )
    object_fields["is_active"] = is_active if is_active is not None else fake.boolean()
    object_fields["date_joined"] = date_joined or fake.date_time_this_year()
    object_fields["last_login"] = last_login or fake.date_time_this_year()

    user = User.objects.create_user(**object_fields)
    return user


def create_users(count: int = DEFAULT_USER_COUNT) -> List[User]:
    """Create a list of user objects

    Args:
        count (int, optional): number of Users to create. Defaults to DEFAULT_USER_COUNT.

    Returns:
        List[User]: list of User objects
    """
    users = []
    for _ in range(count):
        user = create_user()
        users.append(user)
    return users
