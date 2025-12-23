from django.urls import path
from . import views

urlpatterns = [
    # -------------------------
    # User-facing views
    # -------------------------
    path("", views.plans_list, name="plans_list"),
    path("payment/<int:plan_id>/", views.make_payment, name="make_payment"),
    path("my-subscription/", views.my_subscription, name="my_subscription"),

    # -------------------------
    # Promo (AJAX / UX)
    # -------------------------
    path(
        "promo/verify/",
        views.verify_promo_code,
        name="verify_promo_code",
    ),

    # -------------------------
    # Admin / staff views
    # -------------------------
    path(
        "admin/payments/",
        views.admin_payments_list,
        name="admin_payments_list",
    ),
    path(
        "admin/verify-payment/<int:payment_id>/<str:action>/",
        views.verify_payment,
        name="verify_payment",
    ),
]
