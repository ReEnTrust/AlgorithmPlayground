from django.db import models

# Create your models here.
class Feature(models.Model):
    feature_text = models.CharField(max_length=200)

    def __str__(self):
        return self.feature_text

class Item(models.Model):
    item_name = models.CharField(max_length=200)
    item_description = models.CharField(max_length=200)
    item_features = models.ManyToManyField(Feature)

class Customer(models.Model):
    customer_name = models.CharField(max_length=200)

class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    note = models.IntegerField()