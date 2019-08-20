from django.db import models

# Create your models here.

class EntrySurvey(models.Model):
    entry_creation_date = models.DateTimeField(auto_now_add=True)
    entry_url = models.CharField(max_length=200)

    def __str__(self):
        return str(self.id)+" has been sent to "+str(self.entry_url)