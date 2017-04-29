# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import datetime

from VoxPomona.models import *

# form for signing up
class SignUpForm(forms.ModelForm):
    email = forms.CharField(label='email', max_length=500)
    password = forms.CharField(label='password', max_length=128, widget=forms.PasswordInput)

    #Ensure appropriate email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if len(email) > 29:
            raise forms.ValidationError("Sorry, this email is too large.")
        if not(email.endswith('@pomona.edu')):
            raise forms.ValidationError("Sorry, at this time only people with a Pomona email may create an account.")
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

# form for creating a new petition
class NewPetitionForm(forms.ModelForm):

    class Meta:
        model = Petition
        fields = ('title','summary','category','stu_permission','staff_permission','faculty_permission')

    def __init__(self, *args, **kwargs):
        super(NewPetitionForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class' : 'form-control'})
        self.fields['title'].label = 'Petition Title'
        self.fields['title'].help_text = 'Give your petition a descriptive title.'
        self.fields['title'].initial = ''

        self.fields['summary'].widget.attrs.update({'class' : 'form-control'})
        self.fields['summary'].label = 'Petition Summary'
        self.fields['summary'].help_text = 'Summarize your petition - why should people sign it?'
        self.fields['summary'].initial = ''

        self.fields['category'].widget.attrs.update({'class' : 'form-control'})
        self.fields['category'].label = 'Petition Category'
        self.fields['category'].help_text = 'Select which category your petition best fits under'
        self.fields['category'].initial = 'AC'

        self.fields['stu_permission'].widget.attrs.update({'class' : 'form-control'})
        self.fields['stu_permission'].label = ''
        self.fields['stu_permission'].help_text = 'Student users can...'

        self.fields['staff_permission'].widget.attrs.update({'class' : 'form-control'})
        self.fields['staff_permission'].label = ''
        self.fields['staff_permission'].help_text = 'Staff users can...'

        self.fields['faculty_permission'].widget.attrs.update({'class' : 'form-control'})
        self.fields['faculty_permission'].label = ''
        self.fields['faculty_permission'].help_text = 'Faculty users can...'

# form for creating new clause
class NewClauseForm(forms.ModelForm):
    class Meta:
        model = Sign
        fields = ('userID','petitionID','time')
        model = Clause
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(NewClauseForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class' : 'form-control'})
        self.fields['content'].label = 'Clause text'
        self.fields['content'].initial = ''
        self.fields['content'].help_text = 'Press Enter to save your new clause'

# form for the search function
class SearchForm(forms.ModelForm):

    user = forms.CharField(label =  'user', max_length = 200, required = False)
    keyword = forms.CharField(label = 'keyword', max_length = 500, required = False)

    def clean_user(self):
        user = self.cleaned_data.get('user')
        return user

    def clean_keyword(self):
        keyword = self.cleaned_data.get('keyword')
        return keyword

    # def clean_open_time(self):
    #     open_time = self.cleaned_data.get('open_time')
    #     if open_time:
    #         try:
    #             datetime.strptime(open_time, '%Y-%m-%d')
    #         except ValueError:
    #             raise ValueError("Incorrect data format, should be YYYY-MM-DD")
    #     return open_time

    # def clean_last_updated(self):
    #     last_updated = self.cleaned_data.get('last_updated')
    #     if last_updated:
    #         try:
    #             datetime.strptime(last_updated, '%Y-%m-%d')
    #         except ValueError:
    #             raise ValueError("Incorrect data format, should be YYYY-MM-DD")
    #     return last_updated

    class Meta:
        model = Petition
        fields = ('title','category','open_time','last_updated')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({'class' : 'form-control'})
        self.fields['title'].label = 'Search by petition title'
        self.fields['title'].initial = ''
        self.fields['title'].required = False

        self.fields['category'].empty_label = None
        self.fields['category'].widget.attrs.update({'class' : 'form-control'})
        self.fields['category'].label = 'Search by category'
        self.fields['category'].widget.choices = self.fields['category'].choices
        self.fields['category'].blank = True
        self.fields['category'].required = False

        self.fields['user'].widget.attrs.update({'class' : 'form-control'})
        self.fields['user'].label = 'Search by creator name'
        self.fields['user'].initial = ''
        self.fields['user'].required = False

        self.fields['keyword'].widget.attrs.update({'class' : 'form-control'})
        self.fields['keyword'].label = 'Search by keyword'
        self.fields['keyword'].initial = ''
        self.fields['keyword'].required = False

        self.fields['open_time'].widget.attrs.update({'class' : 'form-control'})
        self.fields['open_time'].label = 'Search for petition opened after'
        self.fields['open_time'].help_text = 'YYYY-MM-DD'
        self.fields['open_time'].initial = ''
        self.fields['open_time'].required = False

        self.fields['last_updated'].widget.attrs.update({'class' : 'form-control'})
        self.fields['last_updated'].label = 'Search for petition updated after'
        self.fields['last_updated'].initial = ''
        self.fields['last_updated'].help_text = 'YYYY-MM-DD'
        self.fields['last_updated'].required = False
