from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model

from .serializers import UserSerializer
from .permissions import CanManipulateUser


class UserViewSet(viewsets.ModelViewSet):
    """
    View set for the user endpoints.
    """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.exclude(username='AnonymousUser').exclude(is_staff=True).all()
    permission_classes = (IsAuthenticated, IsAdminUser, CanManipulateUser)
