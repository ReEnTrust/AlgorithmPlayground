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
    TYPE_CHOICES = [
        ('L', 'Leisure'),
        ('B', 'Business'),
    ]
    type = forms.ChoiceField(choices = TYPE_CHOICES, label="type", widget=forms.Select(), required=True)

    DATA_CHOICES = [
        ('0', 'All equally preferred'),
        ('1', 'Location preferred'),
        ('2', 'Rating preferred'),
        ('3', 'Price preferred'),
    ]
    data = forms.ChoiceField(choices = DATA_CHOICES, label="data", widget=forms.RadioSelect, required=True)


class FeedbackForm(forms.Form):
    comment= forms.CharField(widget=forms.Textarea, required=False)
    FEED_CHOICES = [
        (1, 'Totally disagree'),
        (2, 'Disagree'),
        (3, 'Neutral'),
        (4, 'I do not know'),
        (5, 'Agree'),
        (6, 'Totally agree'),
    ]
    feed = forms.ChoiceField(choices = FEED_CHOICES, label="feed", widget=forms.RadioSelect, required=False)
