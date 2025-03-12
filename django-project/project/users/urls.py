from django.urls import path
from .views import UserCreate, UserDetails

urlpatterns = [
    path("", UserCreate.as_view(), name="user-create"),
    path("<int:pk>/", UserDetails.as_view(), name="user-details"),
]
