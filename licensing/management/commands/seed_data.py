"""
Создаёт начальные данные: продукты, типы лицензий, пользователей (админ и обычный).
Запуск: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from licensing.models import Product, LicenseType, Client

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт продукты, типы лицензий и пользователей (admin, user)"

    def handle(self, *args, **options):
        # Продукты
        products_data = [
            {"name": "Desktop Pro", "code": "DESKTOP-PRO"},
            {"name": "Cloud Suite", "code": "CLOUD-SUITE"},
            {"name": "Mobile App", "code": "MOBILE-APP"},
        ]
        for d in products_data:
            obj, created = Product.objects.get_or_create(code=d["code"], defaults=d)
            self.stdout.write(f"  Product: {obj.name} ({'created' if created else 'exists'})")

        # Типы лицензий
        license_types_data = [
            {
                "name": "TRIAL",
                "description": "Пробный период 14 дней",
                "max_devices": 1,
                "has_expiration": True,
                "duration_days": 14,
                "renewable": True,
            },
            {
                "name": "SUBSCRIPTION",
                "description": "Подписка на год",
                "max_devices": 3,
                "has_expiration": True,
                "duration_days": 365,
                "renewable": True,
            },
            {
                "name": "PERPETUAL",
                "description": "Бессрочная лицензия",
                "max_devices": 5,
                "has_expiration": False,
                "duration_days": None,
                "renewable": False,
            },
        ]
        for d in license_types_data:
            obj, created = LicenseType.objects.get_or_create(name=d["name"], defaults=d)
            self.stdout.write(f"  LicenseType: {obj.name} ({'created' if created else 'exists'})")

        # Пользователи
        users_data = [
            {"username": "admin", "password": "admin123", "is_staff": True, "is_superuser": True},
            {"username": "user", "password": "user123", "is_staff": False, "is_superuser": False},
        ]
        for d in users_data:
            password = d["password"]
            username = d["username"]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "is_staff": d["is_staff"],
                    "is_superuser": d.get("is_superuser", False),
                },
            )
            user.set_password(password)
            user.is_staff = d["is_staff"]
            user.is_superuser = d.get("is_superuser", False)
            user.save()
            Token.objects.get_or_create(user=user)
            self.stdout.write(f"  User: {user.username} (staff={user.is_staff}) ({'created' if created else 'updated'})")

        # Один клиент для примеров
        client, created = Client.objects.get_or_create(
            contact_email="client@example.com",
            defaults={
                "name": "ООО Пример",
                "client_type": Client.COMPANY,
                "country": "RU",
            },
        )
        self.stdout.write(f"  Client: {client.name} ({'created' if created else 'exists'})")

        self.stdout.write(self.style.SUCCESS("Seed data done. Login: admin/admin123 or user/user123"))
