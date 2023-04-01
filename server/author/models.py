from uuid import uuid4

from django.db import models


class Author(models.Model):
    id = models.UUIDField(
        default=uuid4, unique=True, primary_key=True
    )
    title = models.CharField(
        max_length=64, default='Not titled author'
    )
    description = models.CharField(
        max_length=256, default=None, null=True
    )
    albums = models.ManyToManyField(
        to='sound.Album', blank=True
    )

    def __str__(self) -> str:
        return self.title
