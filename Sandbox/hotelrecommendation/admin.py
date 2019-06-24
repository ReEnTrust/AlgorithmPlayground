from django.contrib import admin

# Register your models here.
from .models import User
from .models import Hotel
from .models import LogInstance
from .models import LogAction
from .models import LogComment
from .models import Rating


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_firstname', "user_lastname", 'gender', 'user_age', 'user_disable', 'user_target_price', 'user_is_married', 'user_have_kids','type')
    search_fields = ['id', 'user_firstname',"user_lastname"]
admin.site.register(User,UserAdmin)

class LogInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'log_instance_creation_date')
admin.site.register(LogInstance,LogInstanceAdmin)

class LogActionAdmin(admin.ModelAdmin):
    list_display = ('log_instance_id','log_action_date','log_action_description')
admin.site.register(LogAction,LogActionAdmin)

class LogCommentAdmin(admin.ModelAdmin):
    list_display = ('id','log_about','log_comment', 'log_radio1', 'log_instance_id')
admin.site.register(LogComment,LogCommentAdmin)


class HotelAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel_name', "hotel_address", 'hotel_location', 'hotel_room_type', 'hotel_night_price', 'hotel_swimming_pool', 'hotel_breakfast_available','hotel_disability_access',"hotel_michelin_restaurant",'hotel_user_reviews', 'hotel_latitude', 'hotel_longitude')
    search_fields = ['id', 'hotel_name']
admin.site.register(Hotel,HotelAdmin)

class RatingAdmin(admin.ModelAdmin):
    def getUserName(self):
        concerned_user = Rating.objects.filter(id=self.id).first().rating_user
        return concerned_user.user_firstname+" "+concerned_user.user_lastname+" ("+str(concerned_user.id)+")"
    getUserName.short_description = 'User Name'

    def RatingType(self):
        concerned_rating_type = Rating.objects.filter(id=self.id).first().rating_type
        return "All equal" if concerned_rating_type==0 else "Location preferred" if concerned_rating_type==1 else "Rating preferred" if concerned_rating_type==2 else "Price preferred"
    RatingType.short_description = 'Rating type'

    def getHotelName(self):
        concerned_hotel = Rating.objects.filter(id=self.id).first().rating_hotel
        return concerned_hotel.hotel_name+" ("+str(concerned_hotel.id)+")"
    getHotelName.short_description = 'Hotel Name'

    list_display = ('id', getUserName, getHotelName, 'rating_note', RatingType)
admin.site.register(Rating,RatingAdmin)