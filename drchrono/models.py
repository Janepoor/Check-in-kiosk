from django.db import models
from util import Get
import uuid

class Appointment(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    appt_id = models.CharField(max_length=1024)
    appt_time = models.DateTimeField()
    arrival_time = models.DateTimeField(auto_now_add = True)
    time_seen = models.DateTimeField(blank= True, null = True)
    objects = Get()


class Kiosk(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor_id = models.IntegerField()
    doctor_name = models.CharField(max_length=1024, null=True, blank=True)
    timezone_name = models.CharField(max_length=1024, default='US/Pacific')
    refresh_token = models.CharField(max_length=24)
    access_token = models.CharField(max_length=60)
    expires_in = models.IntegerField()
    expire_check_time = models.DateTimeField(auto_now_add=True)

    hours_before = models.IntegerField(default=4)
    hours_after = models.IntegerField(default=4)

    objects = Get()


class Average_wait(models.Model):
    guid  = models.UUIDField(primary_key= True, default= uuid.uuid4,editable= False)
    doctor_id = models.CharField(max_length= 1024)
    time_sum = models.DurationField(default= 0)
    visit_count = models.IntegerField(default= 0)
    objects = Get()





