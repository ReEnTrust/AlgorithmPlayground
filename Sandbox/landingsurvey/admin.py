from django.contrib import admin
from .models import EntrySurvey
# Register your models here.

class EntrySurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'entry_creation_date','entry_url')
admin.site.register(EntrySurvey,EntrySurveyAdmin)
