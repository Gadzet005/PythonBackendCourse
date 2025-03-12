from django.contrib.auth.models import User
from rest_framework import generics
from users.serializers import UserSerializer, UserCreateSerializer


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserDetails(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
