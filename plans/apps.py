from django.apps import AppConfig


class PlansConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plans"
    def ready(self):
        from .models import SiteSettings
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create()