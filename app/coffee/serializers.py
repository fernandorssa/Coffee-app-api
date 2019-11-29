from rest_framework import serializers

from core.models import Tag, Item, Coffee


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for item objects"""

    class Meta:
        model = Item
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CoffeeSerializer(serializers.ModelSerializer):
    """Serialize a coffee"""
    items = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Item.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Coffee
        fields = (
            'id', 'title', 'items', 'tags', 'time_minutes', 'price', 'link',
        )
        read_only_fields = ('id',)
