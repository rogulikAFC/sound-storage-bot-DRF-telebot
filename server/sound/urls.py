from django.urls import path
from .views import SoundListCreateView, AlbumListCreateView


urlpatterns = [
    path('sounds/', SoundListCreateView.as_view()),
    path('albums/', AlbumListCreateView.as_view()),
]
