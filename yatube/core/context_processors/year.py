from django.utils import timezone


def year(request):
    """Add a date with current year."""

    year = timezone.now().strftime("%Y")
    return {"year": int(year)}
