from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from VoxPomona.models import *


class SignUpForm(forms.ModelForm):
    email = forms.CharField(label='email', max_length=500)
    password = forms.CharField(label='password', max_length=128, widget=forms.PasswordInput)

    #Ensure appropriate email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if len(email) > 29:
            raise forms.ValidationError("Sorry, this email is too large.")
        if email and User.objects.filter(email=email).count():
            raise forms.ValidationError('There is already an account associated with this email.')
        return email

    #Ensure password length
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) <= 6:
            raise forms.ValidationError('Password must be longer than 6 characters.')
        return password

    class Meta:
        model = UserInfo
        fields = ('email', 'name', 'user_type')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class' : 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder' : 'Email'})
        self.fields['email'].label = ''

        self.fields['name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['name'].widget.attrs.update({'placeholder' : 'Full name'})
        self.fields['name'].label = ''

        self.fields['user_type'].widget.attrs.update({'class' : 'form-control'})
        self.fields['user_type'].label = 'User type'
        self.fields['user_type'].help_text = 'Click to select your user type'

        self.fields['password'].widget.attrs.update({'class' : 'form-control'})
        self.fields['password'].widget.attrs.update({'placeholder' : 'Password'})
        self.fields['password'].label = ''

class NewPetitionForm(forms.ModelForm):

    class Meta:
        model = Petition
        fields = ('title','summary','category','stu_permission','staff_permission','faculty_permission')

    def __init__(self, *args, **kwargs):
        super(NewPetitionForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class' : 'form-control'})
        self.fields['title'].label = 'Petition Title'
        self.fields['title'].help_text = 'Give your petition a descriptive title.'

        self.fields['summary'].widget.attrs.update({'class' : 'form-control'})
        self.fields['summary'].label = 'Petition Summary'
        self.fields['summary'].help_text = 'Summarize your petition - why should people sign it?'

        self.fields['category'].widget.attrs.update({'class' : 'form-control'})
        self.fields['category'].label = 'Petition Category'
        self.fields['category'].help_text = 'Select which category your petition best fits under'

        self.fields['stu_permission'].widget.attrs.update({'class' : 'form-control'})
        self.fields['stu_permission'].label = ''
        self.fields['stu_permission'].help_text = 'Student users can...'

        self.fields['staff_permission'].widget.attrs.update({'class' : 'form-control'})
        self.fields['staff_permission'].label = ''
        self.fields['staff_permission'].help_text = 'Staff users can...'

        self.fields['faculty_permission'].widget.attrs.update({'class' : 'form-control'})
        self.fields['faculty_permission'].label = ''
        self.fields['faculty_permission'].help_text = 'Faculty users can...'