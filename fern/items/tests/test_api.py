import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from model_mommy import mommy
from rest_framework.test import APITestCase

from fern.items.models import Item

logger = logging.getLogger(__name__)
User = get_user_model()


class TestItem(APITestCase):
    '''Test API: /api/v1/items - /api/v1/items/{id} and their related methods'''

    def setUp(self):
        self.user = mommy.make(User)

    def tearDown(self):
        User.objects.all().delete()

    def test_get_items(self):
        '''Test retriving items '''
        mommy.make(Item, _quantity=5)
        url = '/api/v1/items/'
        self.client.force_login(self.user)
        response = self.client.get(url)
        logger.info(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_get_single_item(self):
        '''Test retriving a single item'''
        item = mommy.make(Item, id=5, name='Jacket')
        url = '/api/v1/items/5'
        self.client.force_login(self.user)
        response = self.client.get(url)
        logger.info(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], item.name)

    def test_put_single_item(self):
        '''Test setting a single item'''
        item = mommy.make(Item, id=5, name='Jacket')
        data = {
            "id": 5,
            "name": "T-shirt",
            "price": item.price,
            "expiry_time": item.expiry_time
        }
        url = '/api/v1/items/5'
        self.client.force_login(self.user)
        response = self.client.put(url, data, format='json')
        logger.info(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'T-shirt')

    def test_put_single_item_invalid_data(self):
        '''Sad-Path: Test put a single item with invalid data'''
        mommy.make(Item, id=5, name='Jacket')
        data = {
            "id": 5,
            "nameX": "T-shirt",
        }
        url = '/api/v1/items/5'
        self.client.force_login(self.user)
        response = self.client.put(url, data, format='json')
        logger.info(response.data)
        self.assertEqual(response.status_code, 400)

    def test_put_single_item_invalid_price_data(self):
        '''Sad-Path: Test put a single item with invalid data'''
        mommy.make(Item, id=5, name='Jacket')
        data = {
            "id": 5,
            "name": "T-shirt",
            "price": -50
        }
        url = '/api/v1/items/5'
        self.client.force_login(self.user)
        response = self.client.put(url, data, format='json')
        logger.info(response.data)
        self.assertEqual(response.status_code, 400)

    def test_put_single_item_with_expiry_time(self):
        '''Test put a single eligable for expiry item'''
        expiry_date = timezone.now() + timedelta(minutes=5)
        mommy.make(Item, id=5, name='Jacket')
        data = {
            "id": 5,
            "name": "T-shirt",
            "price": 15,
            "expiry_time": expiry_date
        }
        url = '/api/v1/items/5?expire_in=60'
        self.client.force_login(self.user)
        response = self.client.put(url, data, format='json')
        logger.info(response.data)
        self.assertEqual(response.status_code, 200)

    def test_get_expired_item(self):
        '''Test get an expired item'''
        expiry_date = timezone.now() - timedelta(minutes=5)
        mommy.make(Item, id=5, name='Jacket', expiry_time=expiry_date)
        url = '/api/v1/items/5'
        self.client.force_login(self.user)
        response = self.client.get(url)
        logger.info(response.data)
        self.assertEqual(response.status_code, 404)

    def test_head_expired_item(self):
        '''Test head an expired item'''
        expiry_date = timezone.now() - timedelta(minutes=5)
        mommy.make(Item, id=5, name='Jacket', expiry_time=expiry_date)
        url = '/api/v1/items/5'
        self.client.force_login(self.user)
        response = self.client.head(url)
        logger.info(response.data)
        self.assertEqual(response.status_code, 404)

    def test_head_valid_item(self):
        '''Test check an existing item'''
        mommy.make(Item, id=5, name='Jacket')
        url = '/api/v1/items/5'
        self.client.force_login(self.user)
        response = self.client.head(url)
        logger.info(response.data)
        self.assertEqual(response.status_code, 200)

    def test_delete_single_item(self):
        '''Test delete a single item'''
        mommy.make(Item, id=5, name='Jacket')
        self.client.force_login(self.user)
        url = '/api/v1/items/5'
        response = self.client.delete(url)
        logger.info(response.data)
        self.assertEqual(response.status_code, 204)

    def test_delete_many_items(self):
        '''Test delete many items'''
        mommy.make(Item, _quantity=6)
        self.client.force_login(self.user)
        url = '/api/v1/items/'
        response = self.client.delete(url)
        logger.warning(response.data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(Item.objects.all()), 0)

    def test_get_items_with_filters(self):
        '''Test retriving items using regex filters '''
        mommy.make(Item, name='Jacket')
        mommy.make(Item, name='Jacket blue')
        url = '/api/v1/items/?search=Ja*'
        self.client.force_login(self.user)
        response = self.client.get(url)
        logger.info(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
