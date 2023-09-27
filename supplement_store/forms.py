from django import forms
from captcha.fields import ReCaptchaField

class RegistrationForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'class': 'register-input width100', 'placeholder': 'Email'}), required=True)
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'register-input width100', 'placeholder': 'Username'}), required=True)
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'First Name', 'size': '26'}), required=True)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Last Name', 'size': '26'}), required=True)
    address = forms.CharField(label='Address', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Address', 'size': '26'}), required=True)
    city = forms.CharField(label='Suburb/City', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Suburb/City', 'size': '26'}), required=True)
    state = forms.CharField(label='State/Province', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'State/Province', 'size': '27'}), required=False)
    zipcode = forms.CharField(label='Zip/Postcode', widget=forms.TextInput(attrs={'class': 'register-input width100', 'placeholder': 'Zip/Postcode'}), required=True)
    
    phone = forms.CharField(label='Phone Number', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Phone Number', 'id': 'phone', 'size': '40'}), required=True)
    birthday = forms.DateField(label='Birthday', widget=forms.DateInput(attrs={'class': 'register-input', 'placeholder': 'Birthday', 'type': 'date'}), required=False)
    
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'register-input', 'placeholder': 'Password', 'id': 'password', 'size': '24'}), required=True)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'register-input', 'placeholder': 'Confirm Password', 'id': 'confirm_password', 'size': '24'}), required=True)

    captcha = ReCaptchaField()