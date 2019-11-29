from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Coffee

from coffee.serializers import CoffeeSerializer


COFFEES_URL = reverse('coffee:coffee-list')


def sample_coffee(user, **params):
    """Create and return a sample coffee"""
    defaults = {
        'title': 'Sample coffee',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Coffee.objects.create(user=user, **defaults)


class PublicCoffeeApiTests(TestCase):
    """Test unauthenticated coffee API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(COFFEES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCoffeeApiTests(TestCase):
    """Test unauthenticated coffee API access"""

    def setUp(self):
        self.client = APIClient
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com'
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_coffees(self):
        """Test retrieving a list of coffees"""
        sample_coffee(user=self.user)
        sample_coffee(user=self.user)

        res = self.client.get(COFFEES_URL)

        coffees = Coffee.objects.all().order_by('-id')
        serializer = CoffeeSerializer(coffees, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_coffees_limited_to_user(self):
        """Test retrieving coffees for user"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'password123'
        )
        sample_coffee(user=user2)
        sample_coffee(user=self.user)

        res = self.client.get(COFFEES_URL)

        coffees = Coffee.objects.filter(user=self.user)
        serializer = CoffeeSerializer(coffees, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
