from django.urls import path

app_name = 'socialelicitation'

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    #The page where the user sees his recommendation
    path('<int:log>/<int:numbiter>',views.IterView.as_view(), name='iter_view'),
]