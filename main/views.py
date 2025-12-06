from django.shortcuts import render, redirect
from pyexpat.errors import messages
from user.models import Profile
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from user.models import Contact
from plans.utils import user_is_premium
from plans.models import UserSubscription
from datetime import date
from connect.models import ChatMessage
from connect.models import ConnectionRequest


MAX_FREE_MESSAGES = 20
MAX_FREE_REQUESTS = 5
MAX_FREE_VIEWS = 10   # optional (future feature)


# Create your views here.
def entry_user(request):
    # if request.user.is_active:
    #     # return redirect('dashboard')
    #     pass
    return render(request, 'user/index.html')


@login_required
def redirect_user_dashboard(request):
    user = request.user
    user_name = user.get_full_name() or user.username

    # Ensure profile exists
    try:
        user_profile = user.profile
    except Profile.DoesNotExist:
        messages.error(request, "Kindly complete your profile before proceeding further.")
        return redirect("complete_profile")

    # -----------------------------
    # ⭐ PREMIUM STATUS & USAGE DATA
    # -----------------------------
    is_premium = user_is_premium(user)
    subscription = getattr(user, "subscription", None)

    # Limits
    MAX_FREE_MESSAGES = 20
    MAX_FREE_REQUESTS = 5
    MAX_FREE_VIEWS = 10  # optional, future

    today = date.today()

    # Count today's sent messages
    sent_messages_today = ChatMessage.objects.filter(
        sender=user,
        timestamp__date=today
    ).count()

    remaining_messages = (
        "Unlimited" if is_premium else max(0, MAX_FREE_MESSAGES - sent_messages_today)
    )

    # Count today's connection requests
    sent_requests_today = ConnectionRequest.objects.filter(
        sender=user,
        timestamp__date=today
    ).count()

    remaining_requests = (
        "Unlimited" if is_premium else max(0, MAX_FREE_REQUESTS - sent_requests_today)
    )

    # ----------------------------------
    # ⭐ MATCHED PROFILES (your existing logic)
    # ----------------------------------
    matched_profiles = []
    preferred_genders = get_opposite_gender(user_profile.gender)

    base_query = Profile.objects.exclude(user=user).filter(
        Q(user__first_name__isnull=False) & ~Q(user__first_name='') |
        Q(user__last_name__isnull=False) & ~Q(user__last_name='') |
        Q(user__username__isnull=False) & ~Q(user__username='')
    )

    base_query = base_query.filter(gender__in=preferred_genders)

    if user_profile.age:
        age_min = user_profile.age - 5
        age_max = user_profile.age + 5
        base_query = base_query.filter(age__gte=age_min, age__lte=age_max)

    if user_profile.looking_for:
        base_query = base_query.filter(looking_for__iexact=user_profile.looking_for)

    if user_profile.city:
        base_query = base_query.filter(city__iexact=user_profile.city)

    matched_profiles = base_query.order_by('-created_at')[:5]

    if not matched_profiles:
        fallback_query = Profile.objects.exclude(user=user).filter(
            gender__in=preferred_genders,
            user__is_active=True,
            user__first_name__isnull=False
        )
        matched_profiles = fallback_query[:5]

    # -----------------------------
    # ⭐ BUILD FINAL CONTEXT
    # -----------------------------
    context = {
        "user_name": user_name,
        "matched_profiles": matched_profiles,

        # --- PREMIUM DATA ---
        "is_premium": is_premium,
        "subscription": subscription,
        "plan_name": subscription.plan.name if (subscription and subscription.plan) else None,
        "plan_expiry": subscription.end_date if subscription else None,
        "remaining_messages": remaining_messages,
        "remaining_requests": remaining_requests,
        "max_free_messages": MAX_FREE_MESSAGES,
        "max_free_requests": MAX_FREE_REQUESTS,
    }

    return render(request, "user/user_dashboard.html", context)


def get_opposite_gender(gender):
    if gender == 'Male':
        return ['Female']
    elif gender == 'Female':
        return ['Male']
    return ['Male', 'Female']  # For 'Other' or null fallback


def privacy(request):
    return render(request, 'user/brandfiles/privacypolicy.html')


def terms(request):
    return render(request, 'user/brandfiles/terms.html')


def about(request):
    return render(request, 'user/brandfiles/about.html')


def contact(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST['name']
        message = request.POST['message']
        contact_object = Contact()
        contact_object.message = message
        contact_object.user = user
        contact_object.save()
        messages.success(request, 'Your message has been sent.')
        return redirect('user_dashboard')
    return render(request, 'user/brandfiles/contactus.html')

def faq(request):
    return render(request, 'user/brandfiles/faq.html')

def custom_404_view(request, exception=None):
    if "siteadmin" in request.path:
        return redirect('siteadmin')
    return redirect('login')
