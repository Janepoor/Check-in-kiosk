from django import forms
from util import LANGUAGE_OPTIONS,GENDER_OPTIONS,STATE_OPTIONS,RACE_OPTIONS,ETHNICITY_OPTIONS
#from django.contrib.localflavor.us.us_states import STATE_CHOICES


class AppointmentSelectionForm(forms.Form):
    appt_id = forms.CharField(max_length=1024)

class PatientVerificationForm(forms.Form):
    appt_id = forms.CharField(widget=forms.HiddenInput(),max_length=1024)
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    gender = forms.ChoiceField(choices=GENDER_OPTIONS)
    date_of_birth = forms.DateField(required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}))


class PatientUpdateForm(forms.Form):
    appt_id = forms.CharField(widget=forms.HiddenInput(),max_length=1024)
    #social_security_number = forms.CharField(max_length=11, required=False, label='SSN, if available')
    preferred_language = forms.ChoiceField(choices=LANGUAGE_OPTIONS, required=False, label='Preferred Language')

    cell_phone = forms.CharField(max_length=1024, required=False, label='Mobile/SMS-capable phone')
    home_phone = forms.CharField(max_length=1024, required=False, label='Home Phone')

    address = forms.CharField(max_length=1024, required=False, label='Street',)
    city = forms.CharField(max_length=1024, required=False, label='City')
    state = forms.ChoiceField(choices=STATE_OPTIONS, required=False, label='State')
    zip_code = forms.CharField(max_length=10, required=False, label='ZIP')

    emergency_contact_name = forms.CharField(max_length=1024, required=False, label='Emergency contact: Name')
    emergency_contact_phone = forms.CharField(max_length=1024, required=False, label='Emergency contact: Phone')
    emergency_contact_relation = forms.CharField(max_length=1024, required=False, label='Emergency contact: Relation')

    employer = forms.CharField(max_length=1024, required=False, label='Employer: Name')
    employer_address = forms.CharField(max_length=1024, required=False, label='Employer: Street')
    employer_city = forms.CharField(max_length=1024, required=False, label='Employer: City')
    employer_state = forms.ChoiceField(choices=STATE_OPTIONS, required=False, label='Employer: State')
    employer_zip_code = forms.CharField(max_length=10, required=False, label='Employer: ZIP')

    race = forms.ChoiceField(choices=RACE_OPTIONS, required=False, label='Race')
    ethnicity = forms.ChoiceField(choices=ETHNICITY_OPTIONS, required=False, label='Ethnicity')



