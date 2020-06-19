from django.db import models


class Item(models.Model):
    name = models.CharField(help_text='Item name', max_length=255, null=False)
    price = models.PositiveIntegerField(null=False)
    expiry_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Item: {}".format(self.name)
