from django.contrib import admin
from .models import Payment, PremiumPlan, PlanFeature, UserSubscription, SiteSettings
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html

from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, PremiumPlan, PlanFeature, UserSubscription, SiteSettings

class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "amount", "status", "created_at", "view_screenshot", "approve_button", "reject_button"]
    list_filter = ["status", "plan"]
    search_fields = ["user__username", "transaction_id"]

    def view_screenshot(self, obj):
        if obj.screenshot:
            return format_html('<img src="{}" width="70" style="border-radius:5px;" />', obj.screenshot)
        return "No screenshot"
    view_screenshot.short_description = "Screenshot"

    def approve_button(self, obj):
        if obj.status == "pending":
            return format_html(
                '<a class="button" style="background:#2ecc71;color:white;padding:6px 12px;border-radius:4px;text-decoration:none;" href="{}">Approve</a>',
                f"{obj.id}/approve/"
            )
        return "—"
    approve_button.short_description = "Approve"

    def reject_button(self, obj):
        if obj.status == "pending":
            return format_html(
                '<a class="button" style="background:#e74c3c;color:white;padding:6px 12px;border-radius:4px;text-decoration:none;" href="{}">Reject</a>',
                f"{obj.id}/reject/"
            )
        return "—"
    reject_button.short_description = "Reject"

    # Admin URL handlers
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path("<int:payment_id>/approve/", self.admin_site.admin_view(self.process_approve)),
            path("<int:payment_id>/reject/", self.admin_site.admin_view(self.process_reject)),
        ]
        return custom_urls + urls

    def process_approve(self, request, payment_id):
        payment = Payment.objects.get(id=payment_id)
        payment.approve()
        self.message_user(request, f"Payment approved & subscription activated for {payment.user.username}")
        return redirect("/siteadmin/plans/payment")

    def process_reject(self, request, payment_id):
        payment = Payment.objects.get(id=payment_id)
        payment.reject()
        self.message_user(request, f"Payment rejected for {payment.user.username}")
        return redirect("/siteadmin/plans/payment")

admin.site.register(Payment, PaymentAdmin)


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ["name", "get_plans"]

    def get_plans(self, obj):
        return ", ".join([plan.name for plan in obj.plans.all()])

    get_plans.short_description = "Included in Plans"


@admin.register(PremiumPlan)
class PremiumPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "duration", "is_active", "get_features"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]

    def get_features(self, obj):
        return ", ".join([feature.name for feature in obj.features.all()])

    get_features.short_description = "Features"


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "start_date", "end_date", "is_active"]
    list_filter = ["is_active", "start_date", "end_date"]
    search_fields = ["user__username", "plan__name"]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "qr_image")