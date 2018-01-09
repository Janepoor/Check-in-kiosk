from django import forms
#from django.contrib.localflavor.us.us_states import STATE_CHOICES


class AppointmentSelectionForm(forms.Form):
    appt_id = forms.CharField(max_length=1024)

class PatientVerificationForm(forms.Form):
    appt_id = forms.CharField(widget=forms.HiddenInput(),max_length=1024)
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)

    gender = forms.ChoiceField(choices=(('Male','Male'),
                                        ('Female','Female'),
                                        ('Other','Other')))
    date_of_birth = forms.DateField(required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}))

class PatientUpdateForm(forms.Form):
    appt_id = forms.CharField(widget=forms.HiddenInput(),max_length=1024)

    cell_phone = forms.CharField(max_length=1024, required=False, label='Mobile/SMS-capable phone')
    home_phone = forms.CharField(max_length=1024, required=False, label='Home Phone')
    address = forms.CharField(max_length=1024, required=False, label='Street',)
    city = forms.CharField(max_length=1024, required=False, label='City')
    state = forms.CharField(max_length=1024, required=False, label='State')
    zip_code = forms.CharField(max_length=10, required=False, label='Zip code')

    emergency_contact_name = forms.CharField(max_length=1024, required=False, label='Emergency contact: Name')
    emergency_contact_phone = forms.CharField(max_length=1024, required=False, label='Emergency contact: Phone')
    emergency_contact_relation = forms.CharField(max_length=1024, required=False, label='Emergency contact: Relation')

    employer = forms.CharField(max_length=1024, required=False, label='Employer: Name')
    employer_address = forms.CharField(max_length=1024, required=False, label='Employer: Street')
    employer_city = forms.CharField(max_length=1024, required=False, label='Employer: City')


