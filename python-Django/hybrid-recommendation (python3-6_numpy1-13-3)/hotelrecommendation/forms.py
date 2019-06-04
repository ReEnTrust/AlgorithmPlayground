from django import forms


class UserForm(forms.Form):
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
    ALGO_CHOICES = [
        (1, 'Algorithm 1'),
        (2, 'Algorithm 2'),
        (3, 'Algorithm 3'),
    ]
    algo = forms.ChoiceField(choices = ALGO_CHOICES, label="algo", widget=forms.RadioSelect, required=True)