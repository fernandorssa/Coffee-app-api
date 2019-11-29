from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Item, Coffee
from coffee import serializers


class BaseCoffeeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseCoffeeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ItemViewSet(BaseCoffeeAttrViewSet):
    """Manage items in the database"""
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer


class CoffeeViewSet(viewsets.ModelViewSet):
    """Manage coffees in the database"""
    serializer_class = serializers.CoffeeSerializer
    queryset = Coffee.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the coffees for the authenticated user"""
        return self.queryset.filter(user=self.request.user)
