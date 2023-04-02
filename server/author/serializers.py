from rest_framework import serializers

from .models import Author


class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    albums = serializers.SerializerMethodField('get_albums')
    sounds = serializers.SerializerMethodField('get_sounds')

    def get_albums(self, obj: Author) -> list:
        albums = obj.albums.all()

        return [
            {
                'id': album.id,
                'title': album.title,
                'authors': [
                    {
                        'id': author.id,
                        'title': author.title,
                    }

                    for author in album.get_authors()
                ],
                'cover': album.get_cover_url()
            }

            for album in albums
        ]
    
    def get_sounds(self, obj: Author) -> list:
        sounds = obj.get_sounds()

        return [
            {
                'id': sound.id,
                'title': sound.title,
                'cover': sound.get_cover_url(),
                'sound': sound.get_sound_url()
            }

            for sound in sounds[0:9]
        ]

    class Meta:
        fields = [
            'id', 'title', 'description',
            'albums', 'sounds'
        ]
        model=Author
