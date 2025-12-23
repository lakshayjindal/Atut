from .models import CustomPage
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from plans.models import PremiumPlan
from siteadmin.forms import PremiumPlanCreationForm
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model
from .feild_config import OPERATOR_FIELDS
from .models import OperatorUserCreation
from user.models import Profile

User = get_user_model()

@staff_member_required
def create_premium_plan(request):
    if request.method == "POST":
        form = PremiumPlanCreationForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.save()
            form.save_m2m()  # Save the many-to-many relationship (features)

            messages.success(request, f"Premium Plan '{plan.name}' was created successfully!")
            return redirect("siteadmin_create_plan")  # Or to some admin dashboard
    else:
        form = PremiumPlanCreationForm()

    return render(request, "siteadmin/create_premium_plan.html", {"form": form})


def page_list(request):
    pages = CustomPage.objects.all()
    return render(request, 'siteadmin/page_list.html', {'pages': pages})

def page_edit(request, pk):
    page = get_object_or_404(CustomPage, pk=pk)    
    if request.method == 'POST':
        layout = request.POST.get("layout_json")
        if layout:
            page.layout = json.loads(layout)
            page.save()
            return redirect('custom_page_list')
    return render(request, 'siteadmin/page_edit.html', {'page': page})

def page_render(request, slug):
    page = get_object_or_404(CustomPage, slug=slug)
    return render(request, 'siteadmin/page_render.html', {'page': page, 'layout': page.layout})

@csrf_exempt
def page_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Page')
        slug = request.POST.get('slug', '')
        layout_json = request.POST.get('layout_json', '[]')
        page = CustomPage.objects.create(
            title=title,
            slug=slug,
            layout=json.loads(layout_json)
        )
        return redirect('custom_page_edit', pk=page.pk)

    return render(request, 'siteadmin/page_create.html')


def email_test(request):
    import resend
    resend.api_key = "re_9DT1UEmJ_2rGgUnoRVn98CwLSNrdqMo8b"

    params: resend.Emails.SendParams = {
        "from": "pro.soci.app@gmail.com",
        "to": "pro.soci.app@gmail.com",
        "subject": "Hello World",
        "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
    }
    email = resend.Emails.send(params)
    return email

def split_name(full_name: str):
    if not full_name:
        return "", ""
    parts = full_name.strip().split()
    return parts[0], " ".join(parts[1:])


def is_operator(user):
    return user.is_authenticated and user.is_operator

def get_required_fields():
    """
    Returns set of required field keys.
    """
    return {f["key"] for f in OPERATOR_FIELDS if f.get("required")}


def get_field_model_map():
    """
    Returns mapping: field_key -> model (user/profile/picture)
    """
    return {f["key"]: f["model"] for f in OPERATOR_FIELDS}

@login_required
@user_passes_test(is_operator)
def operator_bulk_entry_page(request):
    """
    Renders the operator bulk data entry UI
    with configurable fields.
    """
    return render(
        request,
        "siteadmin/bulk_entry.html",
        {
            "operator_fields": OPERATOR_FIELDS,
        }
    )

@login_required
@user_passes_test(is_operator)
@require_POST
def operator_bulk_create(request):
    """
    Accepts bulk user data and dynamically creates:
    - User
    - Profile
    - OperatorUserCreation (audit)

    Required fields are enforced server-side
    using operator_fields config.
    """
    try:
        payload = json.loads(request.body)
        entries = payload.get("entries", [])
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON payload"},
            status=400
        )

    if not entries:
        return JsonResponse(
            {"error": "No entries provided"},
            status=400
        )

    required_fields = get_required_fields()
    field_model_map = get_field_model_map()

    created = []
    errors = []

    with transaction.atomic():
        for index, row in enumerate(entries):
            try:
                # -------------------
                # Required validation
                # -------------------
                missing = required_fields - set(row.keys())
                if missing:
                    raise ValueError(f"Missing required fields: {', '.join(missing)}")

                phone = (row.get("phone1") or "").strip()

                if not phone or len(phone) != 10 or not phone.isdigit():
                    raise ValueError("Invalid phone number")

                if User.objects.filter(username=phone).exists():
                    raise ValueError("User with this phone already exists")

                # -------------------
                # User creation
                # -------------------
                first_name, last_name = split_name(row.get("full_name"))

                user = User.objects.create(
                    username=phone,
                    first_name=first_name,
                    last_name=last_name,
                    user_gender=row.get("gender"),
                    is_verified=False,
                    is_operator=False,
                    terms_accepted=True,
                    terms_accepted_on=now(),
                )
                user.set_unusable_password()
                user.save()

                # -------------------
                # Profile creation
                # -------------------
                profile_data = {
                    "user": user
                }

                for key, value in row.items():
                    if field_model_map.get(key) == "profile":
                        profile_data[key] = value or None

                Profile.objects.create(**profile_data)

                # -------------------
                # Operator audit
                # -------------------
                OperatorUserCreation.objects.create(
                    operator=request.user,
                    created_user=user,
                    source="manual_entry"
                )

                created.append({
                    "row": index,
                    "username": user.username
                })

            except Exception as e:
                errors.append({
                    "row": index,
                    "error": str(e)
                })

    return JsonResponse(
        {
            "created": created,
            "errors": errors,
            "total": len(entries),
            "success": len(created),
            "failed": len(errors),
        },
        status=207 if errors else 200
    )
