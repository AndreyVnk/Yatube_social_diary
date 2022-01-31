from django.conf import settings
from django.core.paginator import Paginator


def paginator(request, posts):
    """Paginator."""

    paginator = Paginator(posts, settings.PAGE_SIZE_PAGINATOR)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return page_obj


def paginator_page_2(obj, response, count):
    """Test second page of paginator."""

    posts_count_p2 = count - settings.PAGE_SIZE_PAGINATOR
    if posts_count_p2 > settings.PAGE_SIZE_PAGINATOR:
        return obj.assertEqual(
            len(response.context["page_obj"]), settings.PAGE_SIZE_PAGINATOR
        )
    else:
        return obj.assertEqual(
            len(response.context["page_obj"]), posts_count_p2
        )
