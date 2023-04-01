from uuid import uuid4

from django.db import models, connection
from django.dispatch import receiver

from author.models import Author


class Album(models.Model):
    id = models.UUIDField(
        default=uuid4, unique=True, primary_key=True
    )
    title = models.CharField(
        max_length=64, default='Not titled album'
    )
    cover = models.ImageField(
        upload_to='images/covers/albums'
    )
    sounds = models.ManyToManyField(
        to='Sound'
    )
    
    def __str__(self) -> str:
        return self.title
    
    def get_authors(self) -> list:
        return Author.objects.filter(albums__in=[self])


@receiver(models.signals.pre_save, sender=Album)
def handle_album_save(sender: Album, instance: Album, **kwargs):
    authors = [author for sound in instance.sounds.all() for author in sound.authors.all()]

    for author in authors:
        author.albums.add(instance)

@receiver(models.signals.pre_delete, sender=Album)
def handle_album_delete(sender: Album, instance: Album, **kwargs):
    instance.sounds.all().delete()
    instance.cover.delete(False)



class Sound(models.Model):
    id = models.UUIDField(
        default=uuid4, unique=True, primary_key=True
    )
    title = models.CharField(
        max_length=64, default='Not titled sound'
    )
    authors = models.ManyToManyField(
        'author.Author'
    )
    sound = models.FileField(
        upload_to='files/sounds'
    )
    cover = models.ImageField(
        upload_to='images/covers/sounds', null=True, blank=True
    )

    def __str__(self) -> str:
        return f'{self.title}, {self.authors.all()[0].title}'
    

@receiver(models.signals.pre_delete, sender=Sound)
def handle_sound_delete(sender: Sound, instance: Sound, **kwargs):
    if instance.cover:
        instance.cover.delete(False)
    
    instance.sound.delete(False)
