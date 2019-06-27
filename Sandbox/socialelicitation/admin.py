from django.contrib import admin
from socialelicitation.models import LogAction, LogInstance
# Register your models here.

class LogInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'log_instance_creation_date')
admin.site.register(LogInstance,LogInstanceAdmin)

class LogActionAdmin(admin.ModelAdmin):
    list_display = ('log_instance_id','log_action_date','log_action_description')
admin.site.register(LogAction,LogActionAdmin)
