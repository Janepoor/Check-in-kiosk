# Create your views here.
import datetime, requests, urllib, urllib2,logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import  login_required
from django.contrib.auth import logout
import dateutil.parser
from django.utils import timezone

from drchrono.models import Kiosk, Appointment, Average_wait
from drchrono.forms import AppointmentSelectionForm, PatientVerificationForm, PatientUpdateForm
from util import updateKoisk,updateWaiting,access_status,call_api,patch_api

POST = 'POST'
API_ADDR = 'https://drchrono.com/api/'
STATUS_OK = True
logger = logging.getLogger('project.checkin-kiosk')



def main(request):

    result = {}
    if not request.user.is_authenticated():
        return render(request, 'index.html', {})

    user_access_status = access_status(request.user)
    if user_access_status != STATUS_OK:
        logout(request)
        return render(request, 'index.html', { 'user_access_status': user_access_status })

    access_token = request.user.social_auth.get(provider = 'drchrono').extra_data['access_token']

    # calling the API
    logger.info('calling the api with %s' )
    try:
        current_doctor = call_api(access_token, API_ADDR + 'users/current')
        doctor_info = call_api(access_token, API_ADDR + 'doctors/' + str(current_doctor['doctor']))

    except urllib2.HTTPError as e:
            logging.info("Http Error with %s" %e)
            logout(request)
            return render(request, 'index.html', { 'user_access_status': False })


    # get kiosk
    kiosk_instance = updateKoisk(request,Kiosk,current_doctor,doctor_info,timezone)
    # get waiting
    updateWaiting(current_doctor,Average_wait)
    logout(request)

    return redirect('kiosk', instance_guid=kiosk_instance.guid)



def kiosk(request, instance_guid):
    instance = Kiosk.objects.get_or_none(guid=instance_guid)

    if not instance:
        return redirect('home')

    date_range = str(datetime.date.today() - datetime.timedelta(hours=24)) + '/' + str(datetime.date.today() + datetime.timedelta(hours=24))

    try:
        appts_response = call_api(instance.access_token,
                              API_ADDR +'appointments',
                              {'doctor': instance.doctor_id, 'date_range': date_range})

        if appts_response == False:
            return redirect('home')
    except urllib2.HTTPError as e:
        logging.info("Http Error with %s" % e)
        return  redirect('home')

    appts_for_day = []
    for appt in appts_response['results']: # returned in order
        if appt['scheduled_time']:
            appt_time = dateutil.parser.parse(appt['scheduled_time'])

            tz = timezone.get_current_timezone()
            appt_time = tz.localize(appt_time)

        if appt['status'] in ('', 'Confirmed') and appt['patient'] :
            appt_object = {}
            appt_object['id'] = appt['id']
            appt_object['patient'] = appt['patient']
            appt_object['scheduled_time'] = appt_time if appt_time else 'Unavailable'
            appts_for_day.append(appt_object)

    appt_info = { 'appts_for_day': appts_for_day, 'instance_guid': instance_guid, 'kiosk_name': instance.doctor_name, 'now': timezone.now() }
    return render(request, 'kiosk.html',appt_info )


def checkin(request, instance_guid):
    if request.method == 'POST':
        form = AppointmentSelectionForm(request.POST)
        if form.is_valid():
            instance = Kiosk.objects.get_or_none(guid=instance_guid)
            if not instance:
                return redirect('home')

            appt_id = form.cleaned_data.get('appt_id')

            appt = call_api(instance.access_token, API_ADDR+'appointments/' + str(appt_id))

            if appt == False:
                return redirect('home')

            if appt['doctor'] != instance.doctor_id or appt['status'] not in ('', 'Confirmed'):
                return redirect('error', instance_guid=instance_guid)

            form = PatientVerificationForm(initial={ 'appt_id': appt_id })
            return render(request, 'verification.html', { 'form': form, 'instance_guid': instance_guid })
        else:
            return redirect('error', instance_guid=instance_guid)
    else:
        return redirect('error', instance_guid=instance_guid)

def update(request, instance_guid):
    if request.method == POST:
        form = PatientVerificationForm(request.POST)

        if form.is_valid():
            instance = Kiosk.objects.get_or_none(guid=instance_guid)
            if not instance:
                return redirect('home')

            appt_id = form.cleaned_data.get('appt_id')
            appt = call_api(instance.access_token, API_ADDR + 'appointments/' + str(appt_id))

            if appt == False:
                return redirect('home')

            if appt['doctor'] != instance.doctor_id or appt['status'] not in ('', 'Confirmed'):
                return redirect('error', instance_guid=instance_guid)

            patient = call_api(instance.access_token, API_ADDR +'patients/' + str(appt['patient']))

            if patient == False:
                return redirect('home')

            if patient['gender'] and patient['gender'] != form.cleaned_data.get('gender'):
                return redirect('error', instance_guid=instance_guid)

            if patient['first_name'] and patient['first_name'] != form.cleaned_data.get('first_name'):
                return redirect('error', instance_guid=instance_guid)

            if patient['last_name'] and patient['last_name'] != form.cleaned_data.get('last_name'):
                return redirect('error', instance_guid=instance_guid)

            if patient['date_of_birth'] and str(patient['date_of_birth']) != str(
                    form.cleaned_data.get('date_of_birth')):
                return redirect('error', instance_guid=instance_guid)

            patient['appt_id'] = appt_id

            update_form = PatientUpdateForm(initial=patient)
            return render(request, 'update.html', {'form': update_form, 'instance_guid': instance_guid})
        else:
            return redirect('error', instance_guid=instance_guid)
    else:
        return redirect('error', instance_guid=instance_guid)


def complete(request, instance_guid):
    if request.method == 'POST':
        form = PatientUpdateForm(request.POST)

        if form.is_valid():
            instance = Kiosk.objects.get_or_none(guid=instance_guid)
            if not instance:
                return redirect('home')

            appt_id = form.cleaned_data.get('appt_id')
            appt = call_api(instance.access_token, API_ADDR +'appointments/' + str(appt_id))

            if appt == False:
                return redirect('home')

            if appt['doctor'] != instance.doctor_id or appt['status'] not in ('', 'Confirmed'):
                return redirect('error', instance_guid=instance_guid)

            patch_api(instance.access_token, 'https://drchrono.com/api/patients/' + str(appt['patient']), form.cleaned_data)
            patch_api(instance.access_token, 'https://drchrono.com/api/appointments/' + str(appt_id), {'status': 'Arrived'})

            new_visit = Appointment(appt_id=appt['id'], doctor_id=instance.doctor_id, patient_id=appt['patient'], appt_time=dateutil.parser.parse(appt['scheduled_time']))
            new_visit.save()

            return render(request, 'complete.html', { 'form': form, 'instance_guid': instance_guid })
        else:
            return render(request, 'update.html', { 'form': form, 'instance_guid': instance_guid })
    else:
        return redirect('error', instance_guid=instance_guid)

@login_required
def doctor(request):
    access_token = request.user.social_auth.get(provider = 'drchrono').extra_data['access_token']

    current_doctor = call_api(access_token, API_ADDR +'users/current')
    doctor_info = call_api(access_token, API_ADDR+ 'doctors/' + str(current_doctor['doctor']))

    if current_doctor != STATUS_OK:
        return redirect('home')

    doctor_id = current_doctor['doctor']

    if request.method == POST:
        form = AppointmentSelectionForm(request.POST)
        if form.is_valid():
            appt_id = form.cleaned_data.get('appt_id')

            url = API_ADDR + 'appointments/'+str(appt_id)
            patch_api(access_token, url, {'status': 'In Session'})

            # update visit info
            appointment = Appointment.objects.get_or_none(appt_id=str(appt_id))
            if appointment:
                appointment.time_seen = timezone.now()
                appointment.save()

                wait_object = Average_wait.objects.get_or_none(doctor_id=doctor_id)

                if wait_object:
                    wait_object.visit_count += 1
                    wait_object.time_sum = wait_object.time_sum +  (appointment.time_seen - appointment.arrival_time)
                    wait_object.save()

    instance = Kiosk.objects.get_or_none(doctor_id=doctor_id)
    if not instance:
        logout(request)
        return redirect('home')

    date_range = str(datetime.date.today() - datetime.timedelta(hours=24)) + '/' + str(
        datetime.date.today() + datetime.timedelta(hours=24))

    appts_response = call_api(instance.access_token, API_ADDR + 'appointments', {'doctor': instance.doctor_id, 'date_range': date_range})

    if appts_response != STATUS_OK:
        return redirect('home')

    appt_time_lower = timezone.now() - datetime.timedelta(hours=24)
    appt_time_upper = timezone.now() + datetime.timedelta(hours=24)
    now = timezone.now()

    appts_for_day = []

    for appt in appts_response['results']:
        # returned in order
        if appt['scheduled_time']:
            appt_time = dateutil.parser.parse(appt['scheduled_time'])

            tz = timezone.get_current_timezone()
            appt_time = tz.localize(appt_time)

        if appt['patient'] and appt_time >= appt_time_lower and appt_time <= appt_time_upper:
            appt_object = {}
            appt_object['status'] = appt['status']
            appt_object['id'] = appt['id']
            appt_object['patient'] = appt['patient']
            appt_object['scheduled_time'] = appt_time if appt_time else 'Unavailable'

            if appt['status'] == 'Arrived':
                appointment = Appointment.objects.get_or_none(appt_id=appt['id'])
                if appointment:
                    appt_object['arrival_time'] = appointment.arrival_time

            if appt['status'] == 'In Session' or appt['status'] == 'Complete':
                appointment = Appointment.objects.get_or_none(appt_id=appt['id'])
                if appointment and appointment.arrival_time and appointment.time_seen:
                    appt_object['wait_time'] = appointment.time_seen - appointment.arrival_time
            appts_for_day.append(appt_object)

    wait_object = Average_wait.objects.get_or_none(doctor_id=doctor_id)
    wait = wait_object.time_sum / wait_object.visit_count if wait_object.visit_count!= 0 else wait_object.time_sum
    result_info = { 'appts_for_day': appts_for_day, 'wait': wait, 'now': now }

    return render(request, 'doctor.html', result_info)

@login_required
def settings(request):
    access_token = request.user.social_auth.get(provider = 'drchrono').extra_data['access_token']
    current_doctor = call_api(access_token, API_ADDR + 'users/current')

    if current_doctor == False:
        return redirect('home')
    doctor_id = current_doctor['doctor']

    if request.method == POST:
        form = AppointmentSelectionForm(request.POST)
        if form.is_valid():
            appt_id = form.cleaned_data.get('appt_id')

            #url = API_ADDR+'appointments/'+str(appt_id)
            #result = patch_api(access_token, url, {'status': 'Cancelled'})

            visit = Appointment.objects.get_or_none(appt_id=str(appt_id))
            if visit:
                visit.delete()

    instance = Kiosk.objects.get_or_none(doctor_id=doctor_id)
    if not instance:
        logout(request)
        return redirect('home')

    date_range = str(datetime.date.today() - datetime.timedelta(hours=instance.hours_before))+'/'+str(datetime.date.today() + datetime.timedelta(hours=instance.hours_after))

    appts_response = call_api(instance.access_token, API_ADDR +'appointments', {'doctor': instance.doctor_id, 'date_range': date_range})

    if appts_response == False:
        return redirect('home')

    appts_for_day = []

    for appt in appts_response['results']: # returned in order
        if appt['scheduled_time']:
            appt_time = dateutil.parser.parse(appt['scheduled_time'])
            tz = timezone.get_current_timezone()
            appt_time = tz.localize(appt_time)

        if appt['patient'] :
            appt_object = {}
            appt_object['status'] = appt['status']
            appt_object['id'] = appt['id']
            appt_object['patient'] = appt['patient']
            appt_object['scheduled_time'] = appt_time if appt_time else "Unavailable"

            appts_for_day.append(appt_object)
    return render(request, 'admin.html', {'appts_for_day': appts_for_day})


@login_required
def internal(request):
    access_token = request.user.social_auth.get(provider = 'drchrono').extra_data['access_token']
    current_doctor = call_api(access_token, API_ADDR + 'users/current')

    if current_doctor == False:
        return redirect('home')

    doctor_id = current_doctor['doctor']

    instance = Kiosk.objects.get_or_none(doctor_id=doctor_id)
    if not instance:
        return redirect('home')
    request.session['django_timezone'] = instance.timezone_name

    return redirect('doctor')

def error(request, instance_guid):
    return render(request, 'error.html', { 'instance_guid': instance_guid })

def leave(request):
    logout(request)
    return redirect('home')


def about(request):
    return render(request, 'about.html')