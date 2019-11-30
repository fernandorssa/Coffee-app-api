from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Coffee, Tag, Item

from coffee.serializers import CoffeeSerializer, CoffeeDetailSerializer


COFFEES_URL = reverse('coffee:coffee-list')


def detail_url(coffee_id):
    """Return coffee detail URL"""
    return reverse('coffee:coffee-detail', args=[coffee_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_item(user, name='Santa Catarina'):
    """Create and return a sample item"""
    return Item.objects.create(user=user, name=name)


def sample_coffee(user, **params):
    """Create and return a sample coffee"""
    defaults = {
        'title': 'Sample coffee',
        'time_minutes': 10,
        'price': 5.00,
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
        self.client = APIClient()
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

    def test_view_coffee_details(self):
        """Test viewing a coffee detail"""
        coffee = sample_coffee(user=self.user)
        coffee.tags.add(sample_tag(user=self.user))
        coffee.items.add(sample_item(user=self.user))

        url = detail_url(coffee.id)
        res = self.client.get(url)

        serializer = CoffeeDetailSerializer(coffee)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_coffee(self):
        """Test creating coffee"""
        payload = {
            'title': 'Café 3 corações',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(COFFEES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        coffee = Coffee.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(coffee, key))

    def test_create_coffee_with_tags(self):
        """Test creating a coffee with tags"""
        tag1 = sample_tag(user=self.user, name='Mundo Novo')
        tag2 = sample_tag(user=self.user, name='Catuaí')
        payload = {
            'title': 'Café Pelé',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(COFFEES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        coffee = Coffee.objects.get(id=res.data['id'])
        tags = coffee.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_coffee_with_items(self):
        """Test creating coffee with items"""
        item1 = sample_item(user=self.user, name='Conilon')
        item2 = sample_item(user=self.user, name='Robusta')
        payload = {
            'title': 'Orfeu',
            'items': [item1.id, item2.id],
            'time_minutes': 20,
            'price': 7.00
        }
        res = self.client.post(COFFEES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        coffee = Coffee.objects.get(id=res.data['id'])
        items = coffee.items.all()
        self.assertEqual(items.count(), 2)
        self.assertIn(item1, items)
        self.assertIn(item2, items)
