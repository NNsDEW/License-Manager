from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Client(models.Model):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"
    CLIENT_TYPES = [
        (INDIVIDUAL, "Individual"),
        (COMPANY, "Company"),
    ]

    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="owned_clients",
    )
    name = models.CharField(max_length=255)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES)
    vat_number = models.CharField(max_length=64, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="owned_products",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True)
    versioning_scheme = models.CharField(max_length=32, default="semver")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class LicenseType(models.Model):
    TRIAL = "TRIAL"
    SUBSCRIPTION = "SUBSCRIPTION"
    PERPETUAL = "PERPETUAL"

    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="owned_license_types",
    )
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    max_devices = models.PositiveIntegerField(default=1)
    has_expiration = models.BooleanField(default=True)
    duration_days = models.PositiveIntegerField(blank=True, null=True)
    renewable = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="licensing_licensetype_owner_name_uniq",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Pricing(models.Model):
    ONCE = "ONCE"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

    BILLING_PERIODS = [
        (ONCE, "Once"),
        (MONTHLY, "Monthly"),
        (YEARLY, "Yearly"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    license_type = models.ForeignKey(LicenseType, on_delete=models.CASCADE)
    currency = models.CharField(max_length=8, default="USD")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    billing_period = models.CharField(max_length=16, choices=BILLING_PERIODS, default=ONCE)
    valid_from = models.DateField()
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("product", "license_type", "currency", "billing_period", "valid_from")


class Order(models.Model):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

    STATUSES = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (CANCELLED, "Cancelled"),
        (REFUNDED, "Refunded"),
    ]

    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUSES, default=PENDING)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Order #{self.pk} for {self.client}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    license_type = models.ForeignKey(LicenseType, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)


class License(models.Model):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

    STATUSES = [
        (PENDING, "Pending"),
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    license_type = models.ForeignKey(LicenseType, on_delete=models.PROTECT)
    key = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=16, choices=STATUSES, default=PENDING)
    issued_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    max_activations = models.PositiveIntegerField(default=1)
    current_activations_count = models.PositiveIntegerField(default=0)
    order = models.ForeignKey(Order, blank=True, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.key} ({self.status})"


class LicenseActivation(models.Model):
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"
    BLOCKED = "BLOCKED"

    STATUSES = [
        (ACTIVE, "Active"),
        (DEACTIVATED, "Deactivated"),
        (BLOCKED, "Blocked"),
    ]

    license = models.ForeignKey(License, related_name="activations", on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    activated_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUSES, default=ACTIVE)


class LicenseHistory(models.Model):
    license = models.ForeignKey(License, related_name="history", on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    old_status = models.CharField(max_length=16, blank=True, null=True)
    new_status = models.CharField(max_length=16)
    comment = models.TextField(blank=True, null=True)


class KeyGenerationLog(models.Model):
    license = models.ForeignKey(License, blank=True, null=True, on_delete=models.SET_NULL)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    algorithm = models.CharField(max_length=64)
    request_context = models.JSONField(blank=True, null=True)


class Payment(models.Model):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

    STATUSES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
        (REFUNDED, "Refunded"),
    ]

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    payment_gateway = models.CharField(max_length=64)
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    status = models.CharField(max_length=16, choices=STATUSES, default=PENDING)
    paid_at = models.DateTimeField(blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)


class Invoice(models.Model):
    ISSUED = "ISSUED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

    STATUSES = [
        (ISSUED, "Issued"),
        (PAID, "Paid"),
        (CANCELLED, "Cancelled"),
    ]

    order = models.OneToOneField(Order, related_name="invoice", on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=64, unique=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    file_path = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUSES, default=ISSUED)


class Renewal(models.Model):
    license = models.ForeignKey(License, related_name="renewals", on_delete=models.CASCADE)
    old_end_date = models.DateField()
    new_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, blank=True, null=True, on_delete=models.SET_NULL)


class SupportTicket(models.Model):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

    STATUSES = [
        (OPEN, "Open"),
        (IN_PROGRESS, "In progress"),
        (RESOLVED, "Resolved"),
        (CLOSED, "Closed"),
    ]

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    PRIORITIES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    license = models.ForeignKey(License, blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=STATUSES, default=OPEN)
    priority = models.CharField(max_length=16, choices=PRIORITIES, default=MEDIUM)
    created_by = models.ForeignKey(User, related_name="created_tickets", on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        User,
        related_name="assigned_tickets",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SalesAnalytics(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    license_type = models.ForeignKey(LicenseType, on_delete=models.CASCADE)
    total_orders = models.PositiveIntegerField(default=0)
    total_licenses_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    renewals_count = models.PositiveIntegerField(default=0)
    new_clients = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("date", "product", "license_type")


class LicenseUsage(models.Model):
    license = models.ForeignKey(License, on_delete=models.CASCADE)
    date = models.DateField()
    active_devices = models.PositiveIntegerField(default=0)
    last_check_at = models.DateTimeField(blank=True, null=True)
    usage_metadata = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = ("license", "date")


class Notification(models.Model):
    EMAIL = "EMAIL"
    IN_APP = "IN_APP"
    WEBHOOK = "WEBHOOK"

    TYPES = [
        (EMAIL, "Email"),
        (IN_APP, "In-app"),
        (WEBHOOK, "Webhook"),
    ]

    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

    STATUSES = [
        (PENDING, "Pending"),
        (SENT, "Sent"),
        (FAILED, "Failed"),
    ]

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=16, choices=TYPES)
    channel_target = models.CharField(max_length=255, blank=True, null=True)
    template_code = models.CharField(max_length=64)
    payload = models.JSONField()
    status = models.CharField(max_length=16, choices=STATUSES, default=PENDING)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)

