from django.urls import path
from django.conf import settings

from . import views

app_name = 'landingsurvey'

urlpatterns = [

    #The index page
    path('', views.IndexView.as_view(), name='index'),
]