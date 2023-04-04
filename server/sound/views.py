from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import generics

from .serializers import SoundSerializer, AlbumSerializer
from .models import Sound, Album
from author.models import Author


class SoundListCreateView(generics.ListCreateAPIView):
    serializer_class = SoundSerializer
    queryset = Sound.objects.all()
    filterset_fields = ['id']
    search_fields = ['title']

    def perform_create(self, serializer: SoundSerializer, *args, **kwargs):
        data = dict(self.request.data)
        authors_id = data.get('authors')
        sound = self.request.FILES.get('sound')
        cover = self.request.FILES.get('cover')

        with transaction.atomic():
            sound = serializer.save(
                sound=sound,
                cover=cover
            )

            authors = [get_object_or_404(Author, id=id) for id in authors_id]
            sound.authors.set(authors)


class AlbumListCreateView(generics.ListCreateAPIView):
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
    filterset_fields = ['id']
    search_fields = ['title']

    def perform_create(self, serializer: AlbumSerializer, *args, **kwargs):
        data = dict(self.request.data)

        sounds_id = data.get('sounds')
        cover = self.request.FILES.get('cover')

        with transaction.atomic():
            album = serializer.save(
                cover=cover
            )

            sounds = [get_object_or_404(Sound, id=id) for id in sounds_id]
            album.sounds.set(sounds)

            album.save()
    