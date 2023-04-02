from uuid import uuid4
from os.path import basename

from django.db import models
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
    
    def get_cover_url(self) -> str:
        return f'media/images/covers/albums/{basename(self.cover.name)}'


@receiver(models.signals.pre_save, sender=Album)
def handle_album_save(sender: Album, instance: Album, **kwargs):
    current_authors = instance.get_authors()
    authors = [author for sound in instance.sounds.all() for author in sound.authors.all()]

    removed_authors = list(set(current_authors).difference(set(authors)))

    for author in removed_authors:
        author.albums.remove(instance)

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
        return f'{self.title}, {self.authors.all()[0].title if self.authors.all() else "Not titled author"}'
    
    def get_sound_url(self) -> str:
        return f'media/files/sounds/{basename(self.sound.name)}'
    
    def get_album(self) -> bool:
        album = Album.objects.filter(sounds__in=[self])

        if album:
            return album
    
    def get_cover_url(self) -> str:
        album = self.get_album()

        if album:
            return album[0].get_cover_url()
        
        if not album and not self.cover:
            return

        return f'media/images/covers/sounds/{basename(self.cover.name)}'
        

@receiver(models.signals.pre_delete, sender=Sound)
def handle_sound_delete(sender: Sound, instance: Sound, **kwargs):
    if instance.cover:
        instance.cover.delete(False)
    
    instance.sound.delete(False)
