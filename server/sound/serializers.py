from rest_framework import serializers

from .models import Sound, Album


class SoundSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    authors = serializers.SerializerMethodField(
        method_name='get_authors'
    )
    sound_url = serializers.CharField(
        source='get_sound_url', read_only=True
    )
    cover_url = serializers.CharField(
        source='get_cover_url', read_only=True
    )

    def get_authors(self, obj: Sound) -> dict:
        authors = obj.authors.all()
        
        return [
            {
                'id': author.id,
                'title': author.title,
            }
            
            for author in authors
        ]

    class Meta:
        model = Sound
        fields = [
            'id', 'title', 'authors',
            'sound_url', 'cover_url'
        ]


class AlbumSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    cover_url = serializers.CharField(
        source='get_cover_url', read_only=True
    )
    authors = serializers.SerializerMethodField(
        method_name='get_authors'
    )
    sounds = serializers.SerializerMethodField(
        method_name='get_sounds'
    )

    def get_authors(self, obj: Album) -> dict:
        authors = obj.get_authors()

        return [
            {
                'id': author.id,
                'title': author.title,
            }
            
            for author in authors
        ]
    
    def get_sounds(self, obj: Sound) -> dict:
        sounds = obj.sounds.all()

        return [
            {
                'id': sound.id,
                'title': sound.title,
                'sound_url': sound.get_sound_url(),
                'authors': [
                    {
                        'id': author.id,
                        'title': author.title
                    }

                    for author in sound.authors.all()
                ]
            }

            for sound in sounds
        ]

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'authors',
            'cover_url', 'sounds'
        ]
