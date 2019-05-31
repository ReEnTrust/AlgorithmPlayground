from django import forms


class UserForm(forms.Form):
    firstname = forms.CharField(label='Firstname', max_length=100)
    lastname = forms.CharField(label='Lastname', max_length=100)
    age = forms.IntegerField(label='Age')
    target_price= forms.IntegerField(label='Target price')
    physically_disabled = forms.BooleanField(label='Physically disabled', required=False)
    is_married = forms.BooleanField(label = 'Is married', required=False)
    have_kids = forms.BooleanField(label = 'have kids', required=False)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = forms.ChoiceField(choices = GENDER_CHOICES, label="Gender", widget=forms.Select(), required=True)