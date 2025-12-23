from django.db import models
from django.utils.text import slugify
from django.conf import settings
class CustomPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    layout = models.JSONField(default=list)  # stores the page blocks

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class OperatorUserCreation(models.Model):
    """
    Tracks users created or onboarded by an operator.
    Used for auditing, accountability, and performance metrics.
    """

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_users",
        help_text="Operator who performed the data entry"
    )

    created_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_by_operator",
        help_text="User account created by the operator"
    )

    source = models.CharField(
        max_length=50,
        default="manual_entry",
        help_text="Entry source: manual_entry, csv_upload, api_import, etc."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp"
    )

    class Meta:
        verbose_name = "Operator Created User"
        verbose_name_plural = "Operator Created Users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["operator"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["operator", "created_user"],
                name="unique_operator_user_creation"
            )
        ]

    def __str__(self):
        return f"Operator {self.operator.username} → User {self.created_user.username}"
