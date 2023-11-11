from django import forms
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator

class JoinForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    email = forms.CharField(
        widget=forms.TextInput(attrs={'size': '30'}))
    first_name = forms.CharField(
        widget=forms.TextInput())
    last_name = forms.CharField(
        widget=forms.TextInput())
    username = forms.CharField(
        widget=forms.TextInput(),
        validators=[MinLengthValidator(3), MaxLengthValidator(15)]
    )
    lat = forms.DecimalField(widget = forms.HiddenInput(), required = False, label='Latitude', max_digits=22, decimal_places=16)
    lng = forms.DecimalField(widget = forms.HiddenInput(), required = False, label='Longitude', max_digits=22, decimal_places=16)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password')
        help_texts = {'username': None}
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("The given email is already registered.")
        return email
        
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    lat = forms.DecimalField(widget = forms.HiddenInput(), required = False, label='Latitude', max_digits=22, decimal_places=16)
    lng = forms.DecimalField(widget = forms.HiddenInput(), required = False, label='Longitude', max_digits=22, decimal_places=16)

class DistancePreferenceForm(forms.Form):
    distance = forms.ChoiceField(choices=[
        (1, 'exact'),
        (6, 'hide'),
        (2, '500m'),
        (3, '1000m'),
        (4, '2500m'),
        (5, '5000m'),
    ])

class IconPreferenceForm(forms.Form):
    icon = forms.ChoiceField(choices=[(i, i) for i in range(0, 16)])

class ColorPreferenceForm(forms.Form):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
