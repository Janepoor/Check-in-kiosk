from django.db import models
import uuid

# Create your models here.

class Appoinment(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    appoinment_id = models.CharField(max_length=1024)
    appoinment_time = models.DateTimeField()
    arrival_time = models.DateTimeField(auto_now_add = True)
    time_seen = models.DateTimeField(blank= True, null = True)

    objects = GetManager()


class Average_wait(models.Model):
    guid  = models.UUIDField(primary_key= True, default= uuid.uuid4,editable= False)
    doctor_id = models.CharField(max_length= 1024)
    time_sum = models.DurationField(default= 0)
    visit_count = models.IntegerField(default= 0)
    objects = GetManager()

class GetManager(models.Manager):
    def get_or_none(self,**kwargs):
        try:
            return self.get(**kwargs)
        except self.DoesNotExist:
            return None
