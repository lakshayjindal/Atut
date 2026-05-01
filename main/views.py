from django.shortcuts import render, redirect
from user.models import Profile
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from user.models import Contact
from plans.utils import user_is_premium
from plans.models import UserSubscription
from datetime import date
from connect.models import ChatMessage, ConnectionRequest

MAX_FREE_MESSAGES = 20
MAX_FREE_REQUESTS = 5


def entry_user(request):
    return render(request, 'user/index.html')


@login_required
def redirect_user_dashboard(request):
    user = request.user

    # Ensure profile exists — single query
    try:
        user_profile = user.profile
    except Profile.DoesNotExist:
        messages.error(request, "Kindly complete your profile before proceeding.")
        return redirect("complete_profile_step1")

    user_name = user.get_full_name() or user.username
    is_premium = user_is_premium(user)
    subscription = getattr(user, "subscription", None)
    today = date.today()

    # Batch both counts in one query each (only for free users)
    if is_premium:
        remaining_messages = "Unlimited"
        remaining_requests = "Unlimited"
    else:
        sent_today = ChatMessage.objects.filter(sender=user, timestamp__date=today).count()
        reqs_today = ConnectionRequest.objects.filter(sender=user, timestamp__date=today).count()
        remaining_messages = max(0, MAX_FREE_MESSAGES - sent_today)
        remaining_requests = max(0, MAX_FREE_REQUESTS - reqs_today)

    # Matched profiles — prefer local city, fall back to gender match
    preferred_genders = _opposite_gender(user_profile.gender)
    base_qs = (
        Profile.objects
        .exclude(user=user)
        .filter(gender__in=preferred_genders, user__is_active=True)
        .select_related('user')
    )

    if user_profile.looking_for:
        base_qs = base_qs.filter(looking_for__iexact=user_profile.looking_for)

    # Try city + age window first
    matched = []
    if user_profile.city and user_profile.age:
        matched = list(
            base_qs.filter(
                city__iexact=user_profile.city,
                age__gte=user_profile.age - 5,
                age__lte=user_profile.age + 5,
            ).order_by('-id')[:10]
        )

    # Fallback: any active opposite-gender profiles
    if not matched:
        matched = list(base_qs.order_by('-id')[:10])

    context = {
        "user_name": user_name,
        "matched_profiles": matched,
        "has_accepted_terms": user.terms_accepted,
        "is_premium": is_premium,
        "plan_name": subscription.plan.name if subscription and subscription.plan else None,
        "plan_expiry": subscription.end_date if subscription else None,
        "remaining_messages": remaining_messages,
        "remaining_requests": remaining_requests,
        "max_free_messages": MAX_FREE_MESSAGES,
        "max_free_requests": MAX_FREE_REQUESTS,
        "has_verified_badge": bool(subscription and subscription.has_active_subscription),
        "can_view_phone": is_premium,
        "can_request_phone": is_premium,
    }
    return render(request, "user/user_dashboard.html", context)


def _opposite_gender(gender):
    if gender == 'Male':
        return ['Female']
    if gender == 'Female':
        return ['Male']
    return ['Male', 'Female', 'Other']


def privacy(request):
    return render(request, 'user/brandfiles/privacypolicy.html')


def terms(request):
    return render(request, 'user/brandfiles/terms.html')


def about(request):
    return render(request, 'user/brandfiles/about.html')


def contact(request):
    if request.method == 'POST':
        Contact.objects.create(
            user=request.user,
            message=request.POST.get('message', '').strip(),
        )
        messages.success(request, 'Your message has been sent.')
        return redirect('user_dashboard')
    return render(request, 'user/brandfiles/contactus.html')


def faq(request):
    return render(request, 'user/brandfiles/faq.html')


def custom_404_view(request, exception=None):
    if "siteadmin" in request.path:
        return redirect('siteadmin')
    return redirect('login')
