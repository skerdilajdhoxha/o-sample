from django.db import models


class TimeStampedModel(models.Model):
    """
       An abstract base class model that provides self-updating
       ``created`` and ``updated`` fields.
       """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
