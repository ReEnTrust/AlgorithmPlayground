from django.urls import path
from django.conf import settings

from . import views

app_name = 'hotelrecommendation'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:firstname>/<str:lastname>/<int:age>/<int:target_price>/<str:physically_disabled>/<str:is_married>/<str:have_kids>/<str:gender>',views.ResultView.as_view(), name='result_view'),
]

