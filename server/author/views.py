from django.shortcuts import render
from rest_framework import generics

from .models import Author
from .serializers import AuthorSerializer


class AuthorListCreate(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    search_fields = ['title']
    filterset_fields = ['id']
