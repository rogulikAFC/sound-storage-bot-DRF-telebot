from uuid import uuid4

from django.db import models, connection
from django.dispatch import receiver


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
    authors = models.ManyToManyField(
        to='author.Author', blank=True
    )
    
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        super(Album, self).save(*args,  **kwargs)
        
        sounds = self.sounds.all()
        authors = [author for sound in sounds for author in sound.authors.all()]

        self.authors.clear()
        for author in authors:
            self.authors.add(author)

        print(self.authors.all())


# @receiver(models.signals.pre_save, sender=Album)
# def handle_album_save(sender: Album, instance: Album, **kwargs):
#     if instance.authors.all():
#         print(f'objects {instance.authors.all()}')
#         return

#     sounds = instance.sounds.all()
#     authors = [author for sound in sounds for author in sound.authors.all()]
#     # print(authors)
#     # print(instance.id)

#     instance.authors.set(authors)
#     # instance.save()

#     # print(connection.queries[-1])

#     print(instance.authors.all())

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
