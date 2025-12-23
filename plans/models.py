# plans/models.py
from django.db import models
from user.models import User
from datetime import timedelta, date
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.conf import settings
class PremiumPlan(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ₹999.00
    duration = models.PositiveIntegerField(help_text="Duration in days")  # e.g. 30, 90, 365
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price"]
        verbose_name = "Premium Plan"
        verbose_name_plural = "Premium Plans"

    def __str__(self):
        return f"{self.name} (₹{self.price} / {self.duration} days)"


class PlanFeature(models.Model):

    FEATURE_TYPES = [
        ("max_messages", "Max Messages Per Day"),
        ("max_requests", "Max Connection Requests Per Day"),
        ("max_views", "Max Profile Views Per Day"),
        ("can_view_phone", "Can View Phone Number"),
        ("can_request_phone", "Can Request Phone Number"),
        ("priority_support", "Priority Support"),
        ("verified_badge", "Verified Badge"),
        ("other", "Other (description only)"),
    ]

    name = models.CharField(max_length=50, choices=FEATURE_TYPES)
    value = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Leave blank for boolean features"
    )

    plans = models.ManyToManyField("PremiumPlan", related_name="features", blank=True)

    def __str__(self):
        return f"{self.name}: {self.value or 'Yes'}"


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"

    def __str__(self):
        if self.plan:
            return f"{self.user.username} → {self.plan.name}"
        return f"{self.user.username} → No Plan"

    def activate(self, plan: PremiumPlan):
        """Activate or renew a subscription for a given plan."""
        self.plan = plan
        self.start_date = date.today()
        self.end_date = date.today() + timedelta(days=plan.duration)
        self.is_active = True
        self.save()

    def deactivate(self):
        """Deactivate the subscription (manually or expired)."""
        self.is_active = False
        self.save()

    def has_active_subscription(self):
        """Check if subscription is still valid (date + status)."""
        if self.is_active and self.end_date and self.end_date >= date.today():
            return True
        return False


class SiteSettings(models.Model):
    qr_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    active = models.BooleanField(default=True)
    # Optional: only allow one settings row
    def save(self, *args, **kwargs):
        self.pk = 1  # always use primary key 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Site Settings (QR Code)"
    
class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("flat", "Flat"),
        ("percent", "Percentage"),
    )

    code = models.CharField(
        max_length=12,
        unique=True,
        db_index=True
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,null=True, blank=True
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True, blank=True
    )

    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    min_cart_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_limit = models.BigIntegerField(
        default=-1,
        help_text="-1 means unlimited total usage"
    )

    per_user_limit = models.PositiveIntegerField(
        default=1
    )

    used_count = models.PositiveBigIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["expires_on"]),
            models.Index(fields=["is_active"]),
        ]

    def is_expired(self):
        return self.expires_on <= timezone.now()

    def can_be_used(self):
        if self.is_deleted or not self.is_active:
            return False
        if self.is_expired():
            return False
        if self.total_limit == -1:
            return True
        return self.used_count < self.total_limit

    def __str__(self):
        return self.code
    
class PromoCodeUsage(models.Model):
    promo = models.ForeignKey(
        PromoCode,
        on_delete=models.PROTECT,
        related_name="usages"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    order_id = models.UUIDField()
    cart_value = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["promo", "user", "order_id"],
                name="unique_promo_use_per_order"
            )
        ]

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("review", "Under Review"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    plan = models.ForeignKey(
        PremiumPlan,
        on_delete=models.PROTECT,
        related_name="payments",
        null=True
    )

    promo = models.ForeignKey(
        PromoCode,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base plan price at time of payment",
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Discount applied via promo code",
        null=True, blank=True
    )

    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final payable amount after discount",
        null=True, blank=True
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="UPI / Bank Transaction ID",
    )

    screenshot = models.URLField(
        blank=True,
        null=True,
        help_text="Uploaded payment proof URL",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        plan_name = self.plan.name if self.plan else "No Plan"
        return f"Payment #{self.id} - {self.user} - {plan_name}"