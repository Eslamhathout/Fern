from django.test import TestCase

from fern.items.models import Item


class ItemTest(TestCase):
    '''Test creating a model and assuring it's str representation '''

    def create_Item(self, name="Dress", price=100):
        return Item.objects.create(name=name, price=price)

    def test_Item_creation(self):
        item = self.create_Item()
        self.assertTrue(isinstance(item, Item))
        self.assertEqual(item.__str__(), "Item: {}".format(item.name))
