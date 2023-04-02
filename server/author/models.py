from uuid import uuid4

from django.db import models
from django.dispatch import receiver


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


@receiver(models.signals.pre_delete, sender=Author)
def handle_author_delete(sender: Author, instance: Author, *args, **kwargs):
    from sound.models import Sound  # avoid circular import

    sounds = Sound.objects.filter(authors__in=[instance])

    single_sounds = sounds.annotate(
        authors_count=models.Count('authors')
    ).filter(
        authors_count=1
    )

    # print(single_sounds.query)

    print(f'{sounds=}')
    print(f'{single_sounds=}')

    single_sounds.delete()

    not_single_sounds = list(set(sounds).difference(set(single_sounds)))

    for sound in not_single_sounds:
        sound.authors.remove(instance)
