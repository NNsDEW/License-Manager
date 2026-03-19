from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import (
    Client,
    Product,
    LicenseType,
    Pricing,
    Order,
    OrderItem,
    License,
    LicenseActivation,
    LicenseHistory,
    Renewal,
    SupportTicket,
)
from .permissions import IsAdminOrReadOnly, IsAdminOrReadCreateOrOwner
from .serializers import (
    ClientSerializer,
    ProductSerializer,
    LicenseTypeSerializer,
    PricingSerializer,
    OrderSerializer,
    OrderItemSerializer,
    LicenseSerializer,
    LicenseActivationSerializer,
    SupportTicketSerializer,
)
from .utils import calculate_license_dates, generate_license_key


def _timedelta_days(days: int):
    # timezone.timedelta may not exist; use datetime.timedelta
    from datetime import timedelta
    return timedelta(days=days)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.none()  # реальный список в get_queryset()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrReadCreateOrOwner]

    def get_queryset(self):
        qs = Client.objects.all()
        if not self.request.user.is_staff:
            # Обычный пользователь: только свои клиенты
            qs = qs.filter(owner=self.request.user)
        elif self.request.user.is_staff:
            owner_id = self.request.query_params.get("owner")
            if owner_id is not None and owner_id != "":
                try:
                    owner_id_int = int(owner_id)
                    # Админ с фильтром owner: только клиенты конкретного пользователя
                    qs = qs.filter(owner_id=owner_id_int)
                except (ValueError, TypeError):
                    pass
        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadCreateOrOwner]

    def get_queryset(self):
        qs = Product.objects.all()
        if not self.request.user.is_staff:
            # Обычный пользователь: только свои продукты
            qs = qs.filter(owner=self.request.user)
        elif self.request.user.is_staff:
            owner_id = self.request.query_params.get("owner")
            if owner_id is not None and owner_id != "":
                try:
                    owner_id_int = int(owner_id)
                    # Админ с фильтром owner: только продукты конкретного пользователя
                    qs = qs.filter(owner_id=owner_id_int)
                except (ValueError, TypeError):
                    pass
        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()


class LicenseTypeViewSet(viewsets.ModelViewSet):
    queryset = LicenseType.objects.none()
    serializer_class = LicenseTypeSerializer
    permission_classes = [IsAdminOrReadCreateOrOwner]

    def get_queryset(self):
        qs = LicenseType.objects.all()
        if not self.request.user.is_staff:
            # Обычный пользователь: только свои типы лицензий
            qs = qs.filter(owner=self.request.user)
        elif self.request.user.is_staff:
            owner_id = self.request.query_params.get("owner")
            if owner_id is not None and owner_id != "":
                try:
                    owner_id_int = int(owner_id)
                    # Админ с фильтром owner: только типы конкретного пользователя
                    qs = qs.filter(owner_id=owner_id_int)
                except (ValueError, TypeError):
                    pass
        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()


class PricingViewSet(viewsets.ModelViewSet):
    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.none()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Order.objects.all().select_related("client")
        if not self.request.user.is_staff:
            qs = qs.filter(client__owner=self.request.user)
        elif self.request.user.is_staff:
            owner_id = self.request.query_params.get("owner")
            if owner_id is not None and owner_id != "":
                try:
                    owner_id_int = int(owner_id)
                    # Админ с фильтром owner: только заказы клиентов этого пользователя
                    qs = qs.filter(client__owner_id=owner_id_int)
                except (ValueError, TypeError):
                    pass
        return qs


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().select_related("order", "product", "license_type")
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminOrReadOnly]


class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.none()
    serializer_class = LicenseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = License.objects.all().select_related("client", "product", "license_type")
        if not self.request.user.is_staff:
            qs = qs.filter(product__owner=self.request.user)
        elif self.request.user.is_staff:
            owner_id = self.request.query_params.get("owner")
            if owner_id is not None and owner_id != "":
                try:
                    owner_id_int = int(owner_id)
                    # Админ с фильтром owner: только лицензии по продуктам этого пользователя
                    qs = qs.filter(product__owner_id=owner_id_int)
                except (ValueError, TypeError):
                    pass
        return qs


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    Тикеты поддержки.
    Обычный пользователь видит только свои тикеты (created_by = request.user) и может их создавать.
    Админ видит и может редактировать все тикеты.
    """

    queryset = SupportTicket.objects.select_related("client", "license", "created_by", "assigned_to")
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(created_by=user)

    def perform_create(self, serializer):
        # Привязываем автора тикета к текущему пользователю
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_license(self, request):
        """
        Создание лицензии для клиента/продукта/типа лицензии.
        """
        client_id = request.data.get("client_id")
        product_id = request.data.get("product_id")
        license_type_id = request.data.get("license_type_id")
        order_id = request.data.get("order_id")
        max_activations = request.data.get("max_activations")

        if not (client_id and product_id and license_type_id):
            return Response(
                {"detail": "client_id, product_id и license_type_id обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            client = Client.objects.get(pk=client_id)
            product = Product.objects.get(pk=product_id)
            license_type = LicenseType.objects.get(pk=license_type_id)
        except (Client.DoesNotExist, Product.DoesNotExist, LicenseType.DoesNotExist):
            return Response({"detail": "Некорректные идентификаторы"}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff:
            if (product.owner != request.user or license_type.owner != request.user or
                    (client.owner is not None and client.owner != request.user)):
                return Response(
                    {"detail": "Можно генерировать ключи только для своих продуктов, типов лицензий и клиентов"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        order = None
        if order_id:
            try:
                order = Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                return Response({"detail": "Заказ не найден"}, status=status.HTTP_400_BAD_REQUEST)

        start_date, end_date = calculate_license_dates(license_type)

        with transaction.atomic():
            license_obj = License.objects.create(
                client=client,
                product=product,
                license_type=license_type,
                status=License.PENDING,
                start_date=start_date,
                end_date=end_date,
                max_activations=max_activations or license_type.max_devices,
                order=order,
            )
            # need id & issued_at for key payload
            license_obj.refresh_from_db()
            license_obj.key = generate_license_key(license_obj)
            license_obj.status = License.ACTIVE
            license_obj.save(update_fields=["key", "status"])

            LicenseHistory.objects.create(
                license=license_obj,
                old_status=None,
                new_status=License.ACTIVE,
                comment="Initial activation",
            )

        # `generate_license()` возвращает объект `License`, но ViewSet использует
        # SupportTicketSerializer для стандартных операций. Явно сериализуем License.
        serializer = LicenseSerializer(license_obj)
        data = dict(serializer.data)
        data["product"] = license_obj.product.code
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="validate")
    def validate_license(self, request):
        """
        Валидация лицензии и (опционально) регистрация активации устройства.
        """
        key = request.data.get("key")
        product_code = request.data.get("product_code")
        device_id = request.data.get("device_id")
        device_name = request.data.get("device_name")
        ip_address = request.META.get("REMOTE_ADDR")

        if not (key and product_code):
            return Response(
                {"detail": "key и product_code обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            license_obj = License.objects.select_related("product", "license_type").get(
                key=key, product__code=product_code
            )
        except License.DoesNotExist:
            return Response({"valid": False, "reason": "LICENSE_NOT_FOUND"}, status=status.HTTP_200_OK)

        now_date = timezone.now().date()
        if license_obj.status != License.ACTIVE:
            return Response({"valid": False, "reason": f"STATUS_{license_obj.status}"}, status=status.HTTP_200_OK)

        if license_obj.end_date and license_obj.end_date < now_date:
            return Response({"valid": False, "reason": "EXPIRED"}, status=status.HTTP_200_OK)

        activations_qs = LicenseActivation.objects.filter(
            license=license_obj,
            status=LicenseActivation.ACTIVE,
        )

        # регистрация устройства, если передан device_id
        if device_id:
            existing = activations_qs.filter(device_id=device_id).first()
            if not existing:
                if activations_qs.count() >= license_obj.max_activations:
                    return Response(
                        {"valid": False, "reason": "MAX_ACTIVATIONS_REACHED"},
                        status=status.HTTP_200_OK,
                    )
                LicenseActivation.objects.create(
                    license=license_obj,
                    device_id=device_id,
                    device_name=device_name,
                    ip_address=ip_address,
                )
                License.objects.filter(pk=license_obj.pk).update(
                    current_activations_count=activations_qs.count() + 1
                )

        payload = {
            "valid": True,
            "status": license_obj.status,
            "start_date": license_obj.start_date,
            "end_date": license_obj.end_date,
            "max_activations": license_obj.max_activations,
            "current_activations": license_obj.current_activations_count,
            "license_type": license_obj.license_type.name,
            "product": license_obj.product.code,
        }
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="validate-key")
    def validate_license_by_key(self, request):
        """
        Валидация лицензии по одному key (product_code определяется автоматически).
        """
        key = request.data.get("key")
        if not key:
            return Response({"detail": "key обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            license_obj = License.objects.select_related("product").get(key=key)
        except License.DoesNotExist:
            return Response({"valid": False, "reason": "LICENSE_NOT_FOUND"}, status=status.HTTP_200_OK)

        # Переиспользуем текущую реализацию validate_license (она возвращает нужный payload)
        request._full_data = {  # type: ignore[attr-defined]
            "key": key,
            "product_code": license_obj.product.code,
            "device_id": request.data.get("device_id"),
            "device_name": request.data.get("device_name"),
        }
        return self.validate_license(request)

    @action(
        detail=False,
        methods=["post"],
        url_path="public-validate-key",
        permission_classes=[AllowAny],
    )
    def public_validate_license_by_key(self, request):
        """
        Публичная валидация по ключу БЕЗ логина/пароля.
        Используется только для демонстрационной утилиты (demo_check_key.py).
        """
        return self.validate_license_by_key(request)

    @action(detail=True, methods=["post"], url_path="renew")
    def renew_license(self, request, pk=None):
        """
        Продление лицензии: увеличиваем end_date на duration_days (если license_type.renewable).
        Если лицензия истекла — продляем от сегодняшней даты.
        """
        license_obj = self.get_object()

        if not request.user.is_staff and license_obj.product.owner != request.user:
            return Response({"detail": "Нет прав"}, status=status.HTTP_403_FORBIDDEN)

        lt = license_obj.license_type
        if not lt.has_expiration or not lt.duration_days:
            return Response({"detail": "Эта лицензия не имеет срока действия"}, status=status.HTTP_400_BAD_REQUEST)
        if not lt.renewable:
            return Response({"detail": "Этот тип лицензии не продлевается"}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        old_end = license_obj.end_date or today
        base = old_end if old_end >= today else today
        new_end = base + _timedelta_days(int(lt.duration_days))

        license_obj.end_date = new_end
        if license_obj.status in [License.EXPIRED, License.SUSPENDED]:
            license_obj.status = License.ACTIVE
        license_obj.save(update_fields=["end_date", "status"])

        Renewal.objects.create(
            license=license_obj,
            old_end_date=old_end,
            new_end_date=new_end,
            created_by=request.user if request.user.is_authenticated else None,
            order=license_obj.order,
        )
        LicenseHistory.objects.create(
            license=license_obj,
            old_status=None,
            new_status=license_obj.status,
            comment=f"Renewed until {new_end.isoformat()}",
        )
        return Response(
            {"id": license_obj.id, "end_date": license_obj.end_date, "status": license_obj.status},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="deactivate-device")
    def deactivate_device(self, request, pk=None):
        """
        Деактивация конкретного устройства по device_id.
        """
        device_id = request.data.get("device_id")
        if not device_id:
            return Response({"detail": "device_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            license_obj = self.get_object()
        except License.DoesNotExist:
            return Response({"detail": "Лицензия не найдена"}, status=status.HTTP_404_NOT_FOUND)

        activation = LicenseActivation.objects.filter(
            license=license_obj,
            device_id=device_id,
            status=LicenseActivation.ACTIVE,
        ).first()
        if not activation:
            return Response({"detail": "Активация не найдена"}, status=status.HTTP_404_NOT_FOUND)

        activation.status = LicenseActivation.DEACTIVATED
        activation.deactivated_at = timezone.now()
        activation.save(update_fields=["status", "deactivated_at"])

        active_count = LicenseActivation.objects.filter(
            license=license_obj,
            status=LicenseActivation.ACTIVE,
        ).count()
        License.objects.filter(pk=license_obj.pk).update(current_activations_count=active_count)

        return Response({"detail": "Устройство деактивировано"}, status=status.HTTP_200_OK)


class LicenseActivationViewSet(viewsets.ModelViewSet):
    queryset = LicenseActivation.objects.all().select_related("license")
    serializer_class = LicenseActivationSerializer
    permission_classes = [IsAdminOrReadOnly]

from django.shortcuts import render

# Create your views here.
