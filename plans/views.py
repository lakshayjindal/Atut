from datetime import date
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from django.utils import timezone

from .models import (
    PremiumPlan,
    Payment,
    UserSubscription,
    SiteSettings,
    PromoCode,
)

from .services.promo import apply_promo_code
from user.utils import upload_to_supabase

@login_required
def plans_list(request):
    plans = PremiumPlan.objects.filter(is_active=True)
    subscription = getattr(request.user, "subscription", None)

    return render(
        request,
        "plans/premiumplans.html",
        {
            "plans": plans,
            "user_subscription": subscription,
        },
    )

@login_required
def make_payment(request, plan_id):
    plan = get_object_or_404(PremiumPlan, id=plan_id, is_active=True)
    settings = SiteSettings.objects.first()

    if request.method == "POST":
        transaction_id = request.POST.get("transaction_id", "").strip()
        screenshot_file = request.FILES.get("screenshot")
        promo_code = request.POST.get("promo_code", "").strip().upper()

        if not transaction_id and not screenshot_file:
            messages.error(
                request,
                "Please provide a transaction ID or upload a payment screenshot."
            )
            return redirect("make_payment", plan_id=plan.id)

        screenshot_url = ""
        if screenshot_file:
            screenshot_url = upload_to_supabase(screenshot_file, "payments")

        promo = None
        if promo_code:
            promo = PromoCode.objects.filter(
                code=promo_code,
                is_active=True,
                is_deleted=False,
            ).first()

        Payment.objects.create(
            user=request.user,
            plan=plan,
            promo=promo,                   # stored, not consumed
            amount=plan.price,
            discount_amount=0,
            final_amount=plan.price,       # finalized on approval
            transaction_id=transaction_id,
            screenshot=screenshot_url,
            status="pending",
        )

        messages.info(
            request,
            "Payment submitted successfully. It will be verified shortly."
        )
        return redirect("plans_list")

    return render(
        request,
        "plans/make_payment.html",
        {
            "plan": plan,
            "settings": settings,
        },
    )

@login_required
def my_subscription(request):
    subscription = getattr(request.user, "subscription", None)
    payments = request.user.payments.order_by("-created_at")

    return render(
        request,
        "plans/my_subscription.html",
        {
            "subscription": subscription,
            "payments": payments,
        },
    )

@require_GET
@login_required
def verify_promo_code(request):
    code = request.GET.get("code", "").strip().upper()
    cart_value = request.GET.get("cart_value")

    if not code:
        return JsonResponse({"valid": False, "reason": "empty_code"})

    promo = PromoCode.objects.filter(
        code=code,
        is_active=True,
        is_deleted=False,
        expires_on__gt=timezone.now(),
    ).first()

    if not promo:
        return JsonResponse({"valid": False, "reason": "invalid_or_expired"})

    if promo.total_limit != -1 and promo.used_count >= promo.total_limit:
        return JsonResponse({"valid": False, "reason": "exhausted"})

    if cart_value:
        try:
            cart_value = float(cart_value)
            if cart_value < promo.min_cart_value:
                return JsonResponse(
                    {"valid": False, "reason": "min_cart_not_met"}
                )
        except ValueError:
            return JsonResponse(
                {"valid": False, "reason": "invalid_cart_value"}
            )

    return JsonResponse({"valid": True})

def staff_required(view):
    return user_passes_test(lambda u: u.is_staff, login_url="plans_list")(view)

@login_required
@staff_required
def admin_payments_list(request):
    payments = Payment.objects.filter(status="pending").order_by("created_at")

    return render(
        request,
        "plans/admin_payments_list.html",
        {"payments": payments},
    )

@login_required
@staff_required
@transaction.atomic
def verify_payment(request, payment_id, action):
    payment = get_object_or_404(
        Payment.objects.select_for_update(),
        id=payment_id,
    )

    if payment.status != "pending":
        messages.warning(request, "Payment already processed.")
        return redirect("admin_payments_list")

    if action == "approve":
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

        messages.success(
            request,
            f"Payment approved. Final amount ₹{payment.final_amount}"
        )

    elif action == "reject":
        payment.status = "failed"
        payment.save()
        messages.warning(request, "Payment rejected.")

    else:
        return HttpResponseBadRequest("Invalid action")

    return redirect("admin_payments_list")
