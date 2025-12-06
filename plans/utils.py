from datetime import date

def user_is_premium(user):
    if not hasattr(user, "subscription"):
        return False
    sub = user.subscription
    return sub.is_active and sub.end_date and sub.end_date >= date.today()
