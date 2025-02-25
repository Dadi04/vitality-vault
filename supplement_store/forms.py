from django import forms
from django_recaptcha.fields import ReCaptchaField
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from supplement_store.countries import COUNTRIES
from .models import Item

User = get_user_model()

class RegistrationForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'class': 'register-input width100', 'placeholder': 'Email'}), error_messages={'required': 'Please enter your email.'})
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'register-input width100', 'placeholder': 'Username'}), error_messages={'required': 'Please enter your username.'})
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'First Name', 'size': '26'}), error_messages={'required': 'Please enter your first name.'})
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Last Name', 'size': '26'}), error_messages={'required': 'Please enter your last name.'})
    address = forms.CharField(label='Address', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Address', 'size': '26'}), required=False)
    city = forms.CharField(label='Suburb/City', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Suburb/City', 'size': '26'}), required=False)
    state = forms.CharField(label='State/Province', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'State/Province', 'size': '27'}), required=False)
    country = forms.ChoiceField(choices=COUNTRIES.items(), label='Country', widget=forms.Select(attrs={'class': 'register-input', 'id': 'country'}), required=False)
    zipcode = forms.CharField(label='Zip/Postcode', widget=forms.TextInput(attrs={'class': 'register-input width100', 'placeholder': 'Zip/Postcode'}), required=False)
    phone = forms.CharField(label='Phone Number', widget=forms.TextInput(attrs={'class': 'register-input', 'placeholder': 'Phone Number', 'id': 'phone', 'size': '40'}), required=False)
    birthday = forms.DateField(label='Birthday', widget=forms.DateInput(attrs={'class': 'register-input', 'placeholder': 'Birthday', 'type': 'date'}), required=False)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'register-input', 'placeholder': 'Password', 'id': 'password', 'size': '24'}), error_messages={'required': 'Please enter your password.'})
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'register-input', 'placeholder': 'Confirm Password', 'id': 'confirm_password', 'size': '24'}), error_messages={'required': 'Please confirm your password.'})

    captcha = ReCaptchaField(error_messages={'required': 'Please complete the CAPTCHA verification.'})

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
    def clean_email(self):
        email = self.cleaned_data.get('email')    
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email is already taken.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')    
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username
    
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'name', 'fullname', 'category', 'subcategory', 'description',
            'brand', 'price', 'quantity', 'sale_price',
            'sale_start_date', 'sale_end_date', 'weight', 'flavor', 'gender',
            'size', 'color', 'is_new', 'popularity', 'main_image', 'image1', 
            'image2', 'image3',
        ]
