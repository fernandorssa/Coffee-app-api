from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Item

from coffee.serializers import ItemSerializer

ITEMS_URL = reverse('coffee:item-list')


class PublicItemApiTests(TestCase):
    """Test the publicly available items API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(ITEMS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateItemsApiTests(TestCase):
    """Test the private items API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_item_list(self):
        """Test retrieving a list of items"""
        Item.objects.create(user=self.user, name='Minas Gerais')
        Item.objects.create(user=self.user, name='31/12/2019')

        res = self.client.get(ITEMS_URL)

        items = Item.objects.all().order_by('-name')
        serializer = ItemSerializer(items, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_items_limited_to_user(self):
        """Test that only items for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Item.objects.create(user=user2, name='10')
        item = Item.objects.create(user=self.user, name='Arábica')

        res = self.client.get(ITEMS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], item.name)
