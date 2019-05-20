from django.contrib import admin



from .models import Feature
from .models import Item
from .models import Review
from .models import Customer


# Register your models here.



class ItemAdmin(admin.ModelAdmin):
    def getFeatures(self):
        return ", ".join([
            f.feature_text for f in Item.objects.filter(id=self.id)[0].item_features.all()
        ])
    getFeatures.short_description = 'Features'

    list_display = ('id', 'item_name', "item_description", getFeatures, 'item_picture')

admin.site.register(Item,ItemAdmin)

class FeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'feature_text')
admin.site.register(Feature, FeatureAdmin)

class ReviewAdmin(admin.ModelAdmin):

    def getCustomerId(self):
        return Review.objects.filter(id=self.id)[0].customer.id
    getCustomerId.short_description = 'Customer ID'

    def getItemId(self):
        return Review.objects.filter(id=self.id)[0].item.id
    getItemId.short_description = 'Item ID'

    fields = ['customer', 'item', 'note']
    list_display = ('id', getCustomerId, getItemId,'note')
admin.site.register(Review, ReviewAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name')
admin.site.register(Customer,CustomerAdmin)