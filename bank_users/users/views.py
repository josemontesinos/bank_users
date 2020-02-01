from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    View set for the user endpoints.
    """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
