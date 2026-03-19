from rest_framework import serializers

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
    SupportTicket,
)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class LicenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseType
        fields = "__all__"


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = "__all__"


class LicenseActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseActivation
        fields = "__all__"


class LicenseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseHistory
        fields = "__all__"


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = "__all__"
        # `SupportTicketViewSet.perform_create()` проставляет created_by автоматически,
        # поэтому при создании он не должен быть обязательным полем запроса.
        read_only_fields = ("created_by",)

