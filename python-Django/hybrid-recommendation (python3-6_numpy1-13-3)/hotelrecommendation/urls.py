from django.urls import path
from django.conf import settings

from . import views

app_name = 'hotelrecommendation'

urlpatterns = [

    #The index page
    path('', views.IndexView.as_view(), name='index'),

    #The page where the user sees his recommendation
    path('<int:age>/<int:target_price>/<str:physically_disabled>/<str:is_married>/<str:have_kids>/<str:gender>/<int:algo>',views.ResultView.as_view(), name='result_view'),

    #The page where he can see the ratings from a user in the database
    path('<int:age>/<int:target_price>/<str:physically_disabled>/<str:is_married>/<str:have_kids>/<str:gender>/<int:algo>/<int:id_user>',views.ResultRatingUser.as_view(), name='result_user_rating'),
]

