from django import template
from plans.utils import user_is_premium

register = template.Library()

@register.filter
def is_premium(user):
    return user_is_premium(user)
