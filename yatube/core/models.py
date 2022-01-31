from django.db import models


class CreatedModel(models.Model):
    """Abstract model. Adds a created date."""

    created = models.DateTimeField(
        "Дата создания", auto_now_add=True, db_index=True
    )

    class Meta:
        abstract = True
