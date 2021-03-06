from django.db import models
from django.core.validators import int_list_validator
# Create your models here.

class User(models.Model):
    user_firstname = models.CharField(max_length=200)
    user_lastname = models.CharField(max_length=200)
    user_age = models.BigIntegerField()
    user_target_price = models.DecimalField(max_digits=10, decimal_places=4)
    user_disable = models.BooleanField()
    user_is_married = models.BooleanField()
    user_have_kids = models.BooleanField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    TYPE_CHOICES = [
        ('L', 'Leisure'),
        ('B', 'Business'),
    ]
    gender = models.CharField(
        max_length=1,
        choices = GENDER_CHOICES,
        default = 'M',
    )
    type = models.CharField(
        max_length=1,
        choices = TYPE_CHOICES,
        default = 'L',
    )
    def __str__(self):
        disabilitystatus = ("disabled" if self.user_disable else "not_disabled")
        maritalstatus = ("married" if self.user_is_married else "not_married")
        kidsstatus = ("have_kids" if self.user_disable else "no_kids")
        return self.user_firstname+" "+self.user_lastname+" Age:"+str(self.user_age)+" TargetBudget:"+str(self.user_target_price)+" "+disabilitystatus+" "+maritalstatus+" "+kidsstatus


class Hotel(models.Model):
    hotel_name = models.CharField(max_length=200)
    hotel_address = models.CharField(max_length=200)
    hotel_location = models.CharField(max_length=200)
    hotel_latitude = models.DecimalField(max_digits=20, decimal_places=15)
    hotel_location_score = models.DecimalField(max_digits=20, decimal_places=15, default=-1)
    hotel_longitude = models.DecimalField(max_digits=20, decimal_places=15)
    ROOM_TYPE_CHOICES = [
        ('D', 'Double'),
        ('F', 'Family'),
        ('S', 'Single'),
        ('T', 'Twin'),
    ]
    hotel_room_type = models.CharField(
        max_length=1,
        choices = ROOM_TYPE_CHOICES,
        default = 'S',
    )
    hotel_night_price = models.DecimalField(max_digits=10, decimal_places=4)
    hotel_disability_access = models.BooleanField()
    hotel_swimming_pool = models.BooleanField()
    hotel_breakfast_available = models.BooleanField()
    hotel_michelin_restaurant = models.BooleanField()
    hotel_user_reviews = models.BigIntegerField()


    def __str__(self):
        swimmingstatus = ("pool" if self.hotel_swimming_pool else "no_pool")
        disabilitystatus = ("access" if self.hotel_disability_access else "no_access")
        breakfaststatus =("breakfast" if self.hotel_breakfast_available else "no_breakfast")
        michelin = ("michelin" if self.hotel_michelin_restaurant else "no_michelin")
        return self.hotel_name+" "+self.hotel_address+" "+self.hotel_location+" Lat:"+str(self.hotel_latitude)+" Long:"+str(self.hotel_longitude)+" Price:"+str(self.hotel_night_price)+" Review:"+str(self.hotel_user_reviews)+" "+disabilitystatus+" "+swimmingstatus+" "+breakfaststatus+" "+michelin

class Rating(models.Model):
    rating_user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating_hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    rating_note = models.IntegerField()
    rating_type = models.IntegerField(default=-1)

class LogInstance(models.Model):
    log_instance_creation_date = models.DateTimeField(auto_now_add=True)
    log_identification_string = models.CharField(max_length=200, default='not provided')
    def __str__(self):
        return str(self.id)+" "+str(self.log_instance_creation_date)

class LogAction(models.Model):
    log_action_date = models.DateTimeField(auto_now_add=True)
    log_instance_id = models.BigIntegerField()
    log_action_description = models.CharField(max_length=2000)
    def __str__(self):
        return str(self.log_instance_id)+"|"+str(self.log_action_description)+"|"+str(self.log_action_date)

class LogComment(models.Model):
    log_instance_id = models.BigIntegerField(default=-1)
    log_comment = models.CharField(max_length=2000)
    log_radio1 = models.CharField(max_length=2000, default='')
    log_about = models.CharField(max_length=2000)
    def __str__(self):
        return str(self.log_instance_id)+"|"+str(self.log_comment)+"|"+str(self.log_radio1)+"|"+str(self.log_about)

class CacheRecommendation(models.Model):
    cache_recommendation_hotel = models.CharField(validators=[int_list_validator], max_length=100)
    cache_user = models.ForeignKey(User, on_delete=models.CASCADE)
    cache_description = models.CharField(max_length=2000)

class CacheClosest(models.Model):
    cache_user = models.ForeignKey(User, on_delete=models.CASCADE)
    cache_description = models.CharField(max_length=2000)
    cache_method = models.IntegerField()