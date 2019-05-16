from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('recommends/', include('recommends.urls')),
    path('admin/', admin.site.urls),
]
