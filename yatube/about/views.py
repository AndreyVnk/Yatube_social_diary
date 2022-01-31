from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """View about author."""

    template_name = "about/author.html"


class AboutTechView(TemplateView):
    """View about tech."""

    template_name = "about/tech.html"
