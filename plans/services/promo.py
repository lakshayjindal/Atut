# app/services/promo.py

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from plans.models import PromoCode, PromoCodeUsage

@transaction.atomic
def apply_promo_code(*, code: str, user, order_id, cart_value):
    promo = PromoCode.objects.select_for_update().get(
        code=code,
        is_active=True,
        is_deleted=False
    )

    if promo.expires_on <= timezone.now():
        raise ValueError("Promo expired")

    # Per-user limit
    user_usage = PromoCodeUsage.objects.filter(
        promo=promo,
        user=user
    ).count()

    if user_usage >= promo.per_user_limit:
        raise ValueError("User limit exceeded")

    # Global limit
    if promo.total_limit != -1:
        updated = PromoCode.objects.filter(
            id=promo.id,
            used_count__lt=promo.total_limit
        ).update(used_count=F("used_count") + 1)

        if updated == 0:
            raise ValueError("Promo exhausted")

    # Discount calculation
    if promo.discount_type == "percent":
        discount = (cart_value * promo.discount_value) / 100
    else:
        discount = promo.discount_value

    if promo.max_discount:
        discount = min(discount, promo.max_discount)

    PromoCodeUsage.objects.create(
        promo=promo,
        user=user,
        order_id=order_id,
        cart_value=cart_value,
        discount_amount=discount
    )

    return discount
