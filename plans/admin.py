from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.db import transaction

from .models import (
    Payment,
    PremiumPlan,
    PlanFeature,
    UserSubscription,
    SiteSettings,
    PromoCode,
    PromoCodeUsage
)

from .services.promo import apply_promo_code
import string
import random

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "amount",
        "discount_amount",
        "final_amount",
        "promo",
        "status",
        "created_at",
        "view_screenshot",
        "approve_button",
        "reject_button",
    )

    list_filter = ("status", "plan")
    search_fields = ("user__username", "transaction_id")
    readonly_fields = (
        "user",
        "plan",
        "amount",
        "promo",
        "discount_amount",
        "final_amount",
        "transaction_id",
        "screenshot",
        "created_at",
    )

    def view_screenshot(self, obj):
        if obj.screenshot:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="70" style="border-radius:6px;" />'
                '</a>',
                obj.screenshot,
                obj.screenshot,
            )
        return "—"
    view_screenshot.short_description = "Screenshot"

    def approve_button(self, obj):
        if obj.status == "pending":
            url = reverse("admin:plans_payment_approve", args=[obj.id])
            return format_html(
                '<a class="button" style="background:#2ecc71;color:white;" href="{}">Approve</a>',
                url,
            )
        return "—"
    approve_button.short_description = "Approve"

    def reject_button(self, obj):
        if obj.status == "pending":
            url = reverse("admin:plans_payment_reject", args=[obj.id])
            return format_html(
                '<a class="button" style="background:#e74c3c;color:white;" href="{}">Reject</a>',
                url,
            )
        return "—"
    reject_button.short_description = "Reject"

    # ------------------------
    # Custom admin URLs
    # ------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:payment_id>/approve/",
                self.admin_site.admin_view(self.approve_payment),
                name="plans_payment_approve",
            ),
            path(
                "<int:payment_id>/reject/",
                self.admin_site.admin_view(self.reject_payment),
                name="plans_payment_reject",
            ),
        ]
        return custom_urls + urls

    # ------------------------
    # Handlers (SAFE)
    # ------------------------
    @transaction.atomic
    def approve_payment(self, request, payment_id):
        payment = get_object_or_404(
            Payment.objects.select_for_update(),
            id=payment_id,
        )

        if payment.status != "pending":
            self.message_user(
                request,
                "Payment already processed.",
                level=messages.WARNING,
            )
            return redirect(request.META.get("HTTP_REFERER"))

        discount = 0
        if payment.promo:
            discount = apply_promo_code(
                code=payment.promo.code,
                user=payment.user,
                order_id=payment.id,
                cart_value=payment.amount,
            )

        payment.discount_amount = discount
        payment.final_amount = payment.amount - discount
        payment.status = "success"
        payment.save()

        subscription, _ = UserSubscription.objects.get_or_create(
            user=payment.user
        )
        subscription.activate(payment.plan)

        self.message_user(
            request,
            f"Payment approved. Final amount ₹{payment.final_amount}",
            level=messages.SUCCESS,
        )

        return redirect(request.META.get("HTTP_REFERER"))

    @transaction.atomic
    def reject_payment(self, request, payment_id):
        payment = get_object_or_404(
            Payment.objects.select_for_update(),
            id=payment_id,
        )

        if payment.status != "pending":
            self.message_user(
                request,
                "Payment already processed.",
                level=messages.WARNING,
            )
            return redirect(request.META.get("HTTP_REFERER"))

        payment.status = "failed"
        payment.save()

        self.message_user(
            request,
            "Payment rejected.",
            level=messages.WARNING,
        )

        return redirect(request.META.get("HTTP_REFERER"))


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "get_plans")

    def get_plans(self, obj):
        return ", ".join(plan.name for plan in obj.plans.all())

@admin.register(PremiumPlan)
class PremiumPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__username", "plan__name")

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "qr_image")

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_type",
        "discount_value",
        "max_discount",
        "total_limit",
        "used_count",
        "is_active",
        "expires_on",
        "created_on",
    ]

    list_filter = ["is_active", "discount_type", "expires_on"]
    search_fields = ["code"]
    readonly_fields = ["used_count", "created_on"]

    actions = ["generate_promo_codes"]

    def generate_promo_codes(self, request, queryset):
        """
        Admin action: generate fresh promo codes
        Uses the first selected row as a template.
        """
        if queryset.count() != 1:
            self.message_user(
                request,
                "Select exactly ONE promo code as a template.",
                level=messages.ERROR,
            )
            return

        template = queryset.first()

        def generate_code(length=8):
            chars = string.ascii_uppercase + string.digits
            while True:
                code = "".join(random.choices(chars, k=length))
                if not PromoCode.objects.filter(code=code).exists():
                    return code

        # Generate 5 new promo codes by default
        created = []
        for _ in range(5):
            created.append(
                PromoCode(
                    code=generate_code(),
                    discount_type=template.discount_type,
                    discount_value=template.discount_value,
                    max_discount=template.max_discount,
                    min_cart_value=template.min_cart_value,
                    total_limit=template.total_limit,
                    per_user_limit=template.per_user_limit,
                    expires_on=template.expires_on,
                    is_active=True,
                )
            )

        PromoCode.objects.bulk_create(created)

        self.message_user(
            request,
            f"{len(created)} promo codes generated successfully.",
            level=messages.SUCCESS,
        )

    generate_promo_codes.short_description = "Generate promo codes (from selected template)"

@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = [
        "promo",
        "user",
        "order_id",
        "cart_value",
        "discount_amount",
        "used_at",
    ]

    list_filter = ["promo", "used_at"]
    search_fields = ["promo__code", "user__username", "order_id"]

    readonly_fields = [
        "promo",
        "user",
        "order_id",
        "cart_value",
        "discount_amount",
        "used_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
