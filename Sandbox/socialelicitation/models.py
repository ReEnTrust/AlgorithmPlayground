from django.db import models

# Create your models here.

class LogInstance(models.Model):
    log_instance_creation_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)+" "+str(self.log_instance_creation_date)

class LogAction(models.Model):
    log_action_date = models.DateTimeField(auto_now_add=True)
    log_instance_id = models.BigIntegerField()
    log_action_description = models.CharField(max_length=2000)
    def __str__(self):
        return str(self.log_instance_id)+"|"+str(self.log_action_description)+"|"+str(self.log_action_date)