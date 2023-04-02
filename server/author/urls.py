from django.urls import path

from .views import AuthorListCreate


urlpatterns = [
    path('', AuthorListCreate.as_view())
]
