from django.contrib import admin

from .models import Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'get_albums']
    search_fields = ['title']

    def get_albums(self, obj: Author) -> str:
        albums = obj.albums.all()
        return ', '.join(album.title for album in albums)
    
    get_albums.short_description = 'albums'
