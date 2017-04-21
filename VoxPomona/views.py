from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse

#Importing datetime Probably want to delete this later ----------------
import datetime

from VoxPomona.forms import *
from VoxPomona.models import *

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. I'm hungry")

#User Registration
def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # User default
            user = User.objects.create_user(form.cleaned_data.get('email'),
                form.cleaned_data.get('email'), form.cleaned_data.get('password'))
            user.save()

            #Create UserInfo to retain other info
            user_info = UserInfo()
            user_info.email = form.cleaned_data.get('email')
            user_info.name = form.cleaned_data.get('name')
            user_info.user_type = form.cleaned_data.get('user_type')
            user_info.user = user
            user_info.save()


            # redirect to the profile page:
            user = authenticate(username=request.POST.get('email'), password=request.POST.get('password'))
            if user is not None:
                if user.is_active:
                    login(request, user)
            return redirect('/VoxPomona/profile')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

#Logout Out: Simply logs out user and redirects to login
@login_required
def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect('login')

@login_required
def user_profile(request):
    return render(request, 'profile.html')

@login_required
def home(request):
    my_petitions = get_user_petitions(request)
    return render(request, 'home.html', my_petitions)

@login_required
#Start a New Petition
def new_petition_view(request):
    if request.method == 'POST':
        form = NewPetitionForm(request.POST)
        if form.is_valid():
            #Grab this user's info

            user_info = request.user.UserInfo
            #Create New Form
            petition = Petition()
            petition.userID = user_info
            petition.title = form.cleaned_data.get('title')
            petition.summary = form.cleaned_data.get('summary')
            petition.category = form.cleaned_data.get('category')
            petition.stu_permission = form.cleaned_data.get('stu_permission')
            petition.staff_permission = form.cleaned_data.get('staff_permission')
            petition.faculty_permission = form.cleaned_data.get('faculty_permission')
            petition.finalized = False #By default, the petition is not final

            #Need to Change these Default Values
            petition.open_time = datetime.datetime.now()
            petition.close_time = datetime.datetime.now()
            petition.threshold = 10

            petition.save()
            
            return redirect('/VoxPomona/home')
        else:
            return render(request, 'new_petition.html', {'form': form})
    else:
        form = NewPetitionForm()
        return render(request, 'new_petition.html', {'form': form})

@login_required
#Grab Petitions
def get_user_petitions(request):
    user_info = request.user.UserInfo
    petitionL = Petition.objects.filter(userID=user_info.email)

    petIDList = []
    for x in range(0,len(petIDList)):
        petIDList[x] = petitionL[x]

    petDict = dict(zip(petIDList,petitionL))
    return petDict