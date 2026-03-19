import base64
import hmac
import os
from datetime import date
from hashlib import sha256
from typing import Tuple

from django.conf import settings

from .models import License, LicenseType, Product


def _get_license_secret() -> bytes:
    secret = getattr(settings, "LICENSE_SECRET_KEY", None)
    if not secret:
        secret = settings.SECRET_KEY
    return secret.encode("utf-8")


def generate_license_key(license_obj: License) -> str:
    """
    Generate a deterministic license key based on license id and product code.
    """
    product: Product = license_obj.product
    payload = f"{license_obj.pk}:{product.code}:{license_obj.issued_at.isoformat()}".encode("utf-8")
    digest = hmac.new(_get_license_secret(), payload, sha256).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    prefix = product.code[:4].upper()
    return f"{prefix}-{encoded[:20]}"


def calculate_license_dates(license_type: LicenseType) -> Tuple[date | None, date | None]:
    """
    Calculate default start/end dates based on license type configuration.
    """
    if not license_type.has_expiration:
        return None, None
    start = date.today()
    duration = license_type.duration_days or 0
    if duration <= 0:
        return start, None
    end = date.fromordinal(start.toordinal() + duration)
    return start, end

