from django.contrib import admin
from .models import Sound, Album


@admin.register(Sound)
class SoundAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_authors']
    search_fields = ['title__startswith']

    def get_authors(self, obj: Sound) -> str:
        authors = obj.authors.all()
        return ', '.join(author.title for author in authors)
    
    get_authors.short_description = 'authors'



@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    
    # def get_authors(self, obj: Album) -> str:
    #     authors = obj.authors.all()
    #     return ', '.join(author.title for author in authors)
    
    # get_authors.short_description = 'authors'