from functools import wraps
from django.http import HttpResponseForbidden
from .utils import user_is_premium

def premium_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not user_is_premium(request.user):
            return HttpResponseForbidden("This feature requires a premium subscription.")
        return view_func(request, *args, **kwargs)
    return wrapper
