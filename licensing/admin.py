from django.contrib import admin
from django.contrib.auth import get_user_model

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
    Payment,
    Invoice,
    SupportTicket,
    SalesAnalytics,
    LicenseUsage,
    Notification,
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "client_type", "contact_email", "owner")
    search_fields = ("name", "contact_email")
    list_filter = ("client_type", "owner")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active", "owner")
    search_fields = ("name", "code")
    list_filter = ("is_active", "owner")


@admin.register(LicenseType)
class LicenseTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "max_devices", "duration_days", "has_expiration", "renewable", "owner")
    list_filter = ("has_expiration", "renewable", "owner")


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "license_type", "amount", "currency", "billing_period", "valid_from", "valid_to")
    list_filter = ("currency", "billing_period")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "status", "total_amount", "currency", "created_at")
    list_filter = ("status", "currency")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "license_type", "quantity", "total_price")


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "client", "product", "license_type", "status", "end_date")
    search_fields = ("key",)
    list_filter = ("status", "product", "license_type")
    # удаления НЕ запрещены — в админке можно удалять лицензии (ключи)


@admin.register(LicenseActivation)
class LicenseActivationAdmin(admin.ModelAdmin):
    list_display = ("id", "license", "device_id", "status", "activated_at")
    list_filter = ("status",)


@admin.register(LicenseHistory)
class LicenseHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "license", "changed_at", "old_status", "new_status", "changed_by")


@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ("id", "license", "old_end_date", "new_end_date", "created_at", "created_by")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "currency", "status", "paid_at")
    list_filter = ("status", "currency")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "invoice_number", "issue_date", "status")
    list_filter = ("status",)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "client", "status", "priority", "created_at")
    list_filter = ("status", "priority")


@admin.register(SalesAnalytics)
class SalesAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "product", "license_type", "revenue", "total_orders")


@admin.register(LicenseUsage)
class LicenseUsageAdmin(admin.ModelAdmin):
    list_display = ("id", "license", "date", "active_devices")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "status", "scheduled_at", "sent_at")




