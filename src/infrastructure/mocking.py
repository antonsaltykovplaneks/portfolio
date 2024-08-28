import random
from typing import List

from faker import Faker

from accounts.mocking import create_users
from accounts.models import User

from .models import Company, Industry, Project, Technology

fake = Faker()

DEFAULT_COMPANY_COUNT = 10
DEFAULT_INDUSTRY_COUNT = 10
DEFAULT_TECHNOLOGY_COUNT = 10
DEFAULT_PROJECT_COUNT = 10


def create_company(title: str = None) -> Company:
    """Create a company object. Uses Faker to generate random data if not provided.

    Args:
        title (str, optional): title of company. Defaults to None.

    Returns:
        Company: company object
    """
    object_fields = {}
    object_fields["title"] = title or fake.company()
    company = Company.objects.create(**object_fields)
    return company


def create_companies(count: int = DEFAULT_COMPANY_COUNT) -> List[Company]:
    """Create a list of company objects

    Args:
        count (int, optional): Number of Companies to create. Defaults to DEFAULT_COMPANY_COUNT.

    Returns:
        List[Company]: List of company objects
    """
    companies = []
    for _ in range(count):
        company = create_company()
        companies.append(company)
    return companies


def create_industry(title: str = None) -> Industry:
    """Create an industry object. Uses Faker to generate random data if not provided.

    Args:
        title (str, optional): title of Industry. Defaults to None.

    Returns:
        Industry: object of Industry
    """
    object_fields = {}
    object_fields["title"] = title or fake.word()
    industry = Industry.objects.create(**object_fields)
    return industry


def create_industries(count: int = DEFAULT_INDUSTRY_COUNT) -> List[Industry]:
    """Create a list of industry objects

    Args:
        count (int, optional): Number of Industries to create. Defaults to DEFAULT_INDUSTRY_COUNT.

    Returns:
        List[Industry]: List of industry objects
    """
    industries = []
    for _ in range(count):
        industry = create_industry()
        industries.append(industry)
    return industries


def create_technology(title: str = None) -> Technology:
    """Create a technology object. Uses Faker to generate random data if not provided.

    Args:
        title (str, optional): title of Technology. Defaults to None.

    Returns:
        Technology: object of Technology
    """
    object_fields = {}
    object_fields["title"] = title or fake.word()
    technology = Technology.objects.create(**object_fields)
    return technology


def create_technologies(count: int = DEFAULT_TECHNOLOGY_COUNT) -> List[Technology]:
    """Create a list of technology objects

    Args:
        count (int, optional): Number of Technologies to create. Defaults to DEFAULT_TECHNOLOGY_COUNT.

    Returns:
        List[Technology]: List of technology objects
    """
    technologies = []
    for _ in range(count):
        technology = create_technology()
        technologies.append(technology)
    return technologies


def create_project(
    title: str = None,
    description: str = None,
    user_id: int = None,
    industry_id: int = None,
    technology_id: int = None,
) -> Project:
    """Create a project object. Uses Faker to generate random data if not provided.

    Args:
        title (str, optional). Defaults to None.
        description (str, optional). Defaults to None.
        user_id (int, optional). Defaults to None. Acquires a random user if not provided. Creates users if they are not exists.
        industry_id (int, optional). Defaults to None. Acquires a random industry if not provided. Creates industries if they are not exists.
        technology_id (int, optional). Defaults to None. Acquires a random technology if not provided. Creates technologies if they are not exists.

    Returns:
        Project: object of Project
    """
    object_fields = {}
    object_fields["title"] = title or fake.sentence()
    object_fields["description"] = description or fake.text()

    user_exists = User.objects.exists()
    if not user_exists:
        create_users()

    if user_id:
        object_fields["user"] = User.objects.get(id=user_id)
    else:
        object_fields["user"] = random.choice(User.objects.all())

    industry_exists = Industry.objects.exists()
    if not industry_exists:
        create_industry()

    if industry_id:
        object_fields["industry"] = Industry.objects.get(id=industry_id)
    else:
        object_fields["industry"] = random.choice(Industry.objects.all())

    technology_exists = Technology.objects.exists()
    if not technology_exists:
        create_technologies()

    if technology_id:
        object_fields["technology"] = Technology.objects.get(id=technology_id)
    else:
        object_fields["technology"] = random.choice(Technology.objects.all())

    project = Project.objects.create(**object_fields)
    return project


def create_projects(count: int = DEFAULT_PROJECT_COUNT) -> List[Project]:
    """Create a list of project objects

    Args:
        count (int, optional): Number of Projects to create. Defaults to DEFAULT_PROJECT_COUNT.

    Returns:
        List[Project]: List of project objects
    """
    projects = []
    for _ in range(count):
        project = create_project()
        projects.append(project)
    return projects
