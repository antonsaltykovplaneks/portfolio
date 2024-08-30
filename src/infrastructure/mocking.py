import json
import random
from typing import List

from django.core import serializers
from faker import Faker

from accounts.mocking import UserFactory
from accounts.models import User

from .models import Company, Industry, Project, Technology

fake = Faker()

DEFAULT_COMPANY_COUNT = 10
DEFAULT_INDUSTRY_COUNT = 10
DEFAULT_TECHNOLOGY_COUNT = 10
DEFAULT_PROJECT_COUNT = 10


class CompanyFactory:

    @staticmethod
    def create(title: str = None) -> Company:
        """Create a company object. Uses Faker to generate random data if not provided.

        Args:
            title (str, optional): title of company. Defaults to None.

        Returns:
            Company: company object
        """
        object_fields = {"title": title or fake.company()}
        company = Company.objects.create(**object_fields)
        return company

    @staticmethod
    def create_many(count: int = DEFAULT_COMPANY_COUNT) -> List[Company]:
        """Create a list of company objects

        Args:
            count (int, optional): Number of Companies to create. Defaults to DEFAULT_COMPANY_COUNT.

        Returns:
            List[Company]: List of company objects
        """
        companies = [CompanyFactory.create() for _ in range(count)]
        return companies

    @staticmethod
    def export(count: int = DEFAULT_COMPANY_COUNT) -> None:
        """Create a list of company objects and save them to a JSON file

        Args:
            count (int, optional): Number of Companies to create. Defaults to DEFAULT_COMPANY_COUNT.
        """
        companies = Company.objects.all()
        if not companies:
            companies = CompanyFactory.create_many(count)

        companies_json = serializers.serialize("json", companies)

        with open("infrastructure/fixtures/companies.json", "w+") as file:
            json.dump(companies_json, file, indent=4)

    @staticmethod
    def import_json(file_path: str = "infrastructure/fixtures/companies.json") -> None:
        """Import companies from a JSON file

        Args:
            file_path (str): Path to JSON file
        """
        with open(file_path, "r") as file:
            companies_json = json.loads(file.read())
        for company_json in companies_json:
            Company.objects.create(**company_json["fields"])


class IndustryFactory:

    @staticmethod
    def create(title: str = None) -> Industry:
        """Create an industry object. Uses Faker to generate random data if not provided.

        Args:
            title (str, optional): title of Industry. Defaults to None.

        Returns:
            Industry: object of Industry
        """
        object_fields = {"title": title or fake.word()}
        industry = Industry.objects.create(**object_fields)
        return industry

    @staticmethod
    def create_many(count: int = DEFAULT_INDUSTRY_COUNT) -> List[Industry]:
        """Create a list of industry objects

        Args:
            count (int, optional): Number of Industries to create. Defaults to DEFAULT_INDUSTRY_COUNT.

        Returns:
            List[Industry]: List of industry objects
        """
        industries = [IndustryFactory.create() for _ in range(count)]
        return industries

    @staticmethod
    def export(count: int = DEFAULT_INDUSTRY_COUNT) -> None:
        """Create a list of industry objects and save them to a JSON file

        Args:
            count (int, optional): Number of Industries to create. Defaults to DEFAULT_INDUSTRY_COUNT.
        """
        industries = Industry.objects.all()
        if not industries:
            industries = IndustryFactory.create_many(count)

        industries_json = serializers.serialize("json", industries)

        with open("infrastructure/fixtures/industries.json", "w+") as file:
            json.dump(industries_json, file, indent=4)

    @staticmethod
    def import_json(file_path: str = "infrastructure/fixtures/industries.json") -> None:
        """Import industries from a JSON file

        Args:
            file_path (str): Path to JSON file
        """
        with open(file_path, "r") as file:
            industries_json = json.loads(file.read())
        for industry_json in industries_json:
            Industry.objects.create(**industry_json["fields"])


class TechnologyFactory:

    @staticmethod
    def create(title: str = None) -> Technology:
        """Create a technology object. Uses Faker to generate random data if not provided.

        Args:
            title (str, optional): title of Technology. Defaults to None.

        Returns:
            Technology: object of Technology
        """
        object_fields = {"title": title or fake.word()}
        technology = Technology.objects.create(**object_fields)
        return technology

    @staticmethod
    def create_many(count: int = DEFAULT_TECHNOLOGY_COUNT) -> List[Technology]:
        """Create a list of technology objects

        Args:
            count (int, optional): Number of Technologies to create. Defaults to DEFAULT_TECHNOLOGY_COUNT.

        Returns:
            List[Technology]: List of technology objects
        """
        technologies = [TechnologyFactory.create() for _ in range(count)]
        return technologies

    @staticmethod
    def export(count: int = DEFAULT_TECHNOLOGY_COUNT) -> None:
        """Create a list of technology objects and save them to a JSON file

        Args:
            count (int, optional): Number of Technologies to create. Defaults to DEFAULT_TECHNOLOGY_COUNT.
        """
        technologies = Technology.objects.all()
        if not technologies:
            technologies = TechnologyFactory.create_many(count)

        technologies_json = serializers.serialize("json", technologies)

        with open("infrastructure/fixtures/technologies.json", "w+") as file:
            json.dump(technologies_json, file, indent=4)

    @staticmethod
    def import_json(
        file_path: str = "infrastructure/fixtures/technologies.json",
    ) -> None:
        """Import technologies from a JSON file

        Args:
            file_path (str): Path to JSON file
        """
        with open(file_path, "r") as file:
            technologies_json = json.loads(file.read())
        for technology_json in technologies_json:
            Technology.objects.create(**technology_json["fields"])


class ProjectFactory:

    @staticmethod
    def create(
        title: str = None,
        description: str = None,
        user_id: int = None,
        industry_ids: List[int] = None,
        technology_ids: List[int] = None,
    ) -> Project:
        """Create a project object. Uses Faker to generate random data if not provided.

        Args:
            title (str, optional). Defaults to None.
            description (str, optional). Defaults to None.
            user_id (int, optional). Defaults to None. Acquires a random user if not provided. Creates Users if they are not exists.
            industry_id (List[int], optional). Defaults to None. Acquires a random industry if not provided. Creates Industries if they are not exists.
            technology_id (List[int], optional). Defaults to None. Acquires a random technology if not provided. Creates Technologies if they are not exists.

        Returns:
            Project: object of Project
        """
        object_fields = {
            "title": title or fake.sentence(),
            "description": description or fake.text(),
        }

        if not User.objects.exists():
            UserFactory.create_many()

        object_fields["user"] = (
            User.objects.get(id=user_id)
            if user_id
            else random.choice(User.objects.all())
        )

        if not Industry.objects.exists():
            IndustryFactory.create_many()

        industries = (
            Industry.objects.filter(id__in=industry_ids)
            if industry_ids
            else random.sample(list(Industry.objects.all()), random.randint(1, 3))
        )

        if not Technology.objects.exists():
            TechnologyFactory.create_many()

        technologies = (
            Technology.objects.filter(id__in=technology_ids)
            if technology_ids
            else random.sample(list(Technology.objects.all()), random.randint(1, 3))
        )

        project = Project.objects.create(**object_fields)
        project.industries.set(industries)
        project.technologies.set(technologies)
        return project

    @staticmethod
    def create_many(count: int = DEFAULT_PROJECT_COUNT) -> List[Project]:
        """Create a list of project objects

        Args:
            count (int, optional): Number of Projects to create. Defaults to DEFAULT_PROJECT_COUNT.

        Returns:
            List[Project]: List of project objects
        """
        projects = [ProjectFactory.create() for _ in range(count)]
        return projects

    @staticmethod
    def export(count: int = DEFAULT_PROJECT_COUNT) -> None:
        """Create a list of project objects and save them to a JSON file

        Args:
            count (int, optional): Number of Projects to create. Defaults to DEFAULT_PROJECT_COUNT.
        """
        projects = Project.objects.all()
        if not projects:
            projects = ProjectFactory.create_many(count)

        projects_json = serializers.serialize("json", projects)

        with open("infrastructure/fixtures/projects.json", "w+") as file:
            json.dump(projects_json, file, indent=4)

    @staticmethod
    def import_json(file_path: str = "infrastructure/fixtures/projects.json") -> None:
        """Import projects from a JSON file

        Args:
            file_path (str): Path to JSON file
        """
        with open(file_path, "r") as file:
            projects_json = json.loads(file.read())
        for project_json in json.loads(projects_json):
            project_json["fields"]["user"] = User.objects.get(
                id=project_json["fields"]["user"]
            )
            industries = [
                Industry.objects.get(id=industry_id)
                for industry_id in project_json["fields"]["industries"]
            ]
            technologies = [
                Technology.objects.get(id=technology_id)
                for technology_id in project_json["fields"]["technologies"]
            ]
            project_json["fields"].pop("industries")
            project_json["fields"].pop("technologies")

            project = Project.objects.create(**project_json["fields"])
            project.industries.set(industries)
            project.technologies.set(technologies)
    
    @staticmethod
    def import_data(data):
        for project in data:
            project["fields"]["user"] = User.objects.get(id=project["fields"]["user"])
            industries = [
                Industry.objects.get(id=industry_id)
                for industry_id in project
            ]