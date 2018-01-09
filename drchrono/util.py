import datetime,requests,urllib
from django.db import models
# from drchrono.models import Kiosk, Appointment, Average_wait


class Get(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


def access_status(user):
    access_token = user.social_auth.get(provider='drchrono').extra_data['access_token']

    endpoint_scope = [
        'doctors',
        'patients',
        'appointment_profiles',
        'allergies'
    ]
    #endpoint_list = ['https://drchrono.com/api/doctors','https://drchrono.com/api/patients','https://drchrono.com/api/appointment_profiles', 'https://drchrono.com/api/allergies']
    url = 'https://drchrono.com/api/'
    for field in endpoint_scope:
        response = requests.get(url + field, headers={'Authorization': 'Bearer %s' % access_token})
        if response.status_code != 200:
            return False
    return True

def call_api(access_token, url, parameters=None):

    if parameters:
        url = url + '?' + urllib.urlencode(parameters)
    response = requests.get(url, headers={'Authorization': 'Bearer %s' % access_token})
    if response.status_code != 200:
        return False
    return response.json()

def patch_api(access_token, url, data):
    response = requests.patch(url, headers={'Authorization': 'Bearer %s' % access_token}, data=data)
    if response.status_code != 204:
        return False
    return True



def updateKoisk(request,Kiosk,current_doctor,doctor_info, timezone):
    kiosk_instance = Kiosk.objects.get_or_none(doctor_id = current_doctor['doctor'])
    if not kiosk_instance:
        kiosk_instance = Kiosk(doctor_id=current_doctor['doctor'],
                               refresh_token=request.user.social_auth.get(provider='drchrono').extra_data['refresh_token'],
                               access_token=request.user.social_auth.get(provider='drchrono').extra_data['access_token'],
                               expires_in=request.user.social_auth.get(provider='drchrono').extra_data['expires_in'],
                                expire_check_time=timezone.now())

    else:
        kiosk_instance.refresh_token=request.user.social_auth.get(provider='drchrono').extra_data['refresh_token']
        kiosk_instance.access_token=request.user.social_auth.get(provider='drchrono').extra_data['access_token']
        kiosk_instance.expires_in=request.user.social_auth.get(provider='drchrono').extra_data['expires_in']
        kiosk_instance.expire_check_time=timezone.now()
        kiosk_instance.save()

    kiosk_instance.doctor_name = doctor_info['first_name'] + doctor_info['last_name']
    kiosk_instance.save()

    return kiosk_instance



def updateWaiting(current_doctor,Average_wait):
    wait_object = Average_wait.objects.get_or_none(doctor_id=current_doctor['doctor'])
    if not wait_object:
        wait_object = Average_wait(doctor_id=current_doctor['doctor'])
        wait_object.time_sum = datetime.timedelta(0)
        wait_object.visit_count = 0
        wait_object.save()
