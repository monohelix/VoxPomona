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
            return redirect('/profile')
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
    home_info = get_user_petitions(request)
    return render(request, 'home.html', home_info)

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

            signature = Sign()
            signature.userID = user_info
            signature.petitionID = petition
            signature.time = datetime.datetime.now()
            signature.save()
            
            return redirect(petition.get_url())
        else:
            return render(request, 'new_petition.html', {'form': form})
    else:
        form = NewPetitionForm()
        return render(request, 'new_petition.html', {'form': form})

@login_required
#View Petition
def view_petition_view(request,pid):
    user_info = request.user.UserInfo
    this_petition = Petition.objects.get(petitionID=pid)
    pet_clauses = Clause.objects.filter(petitionID=this_petition.petitionID).order_by('index')
    user_type = request.user.UserInfo.user_type
    if user_type == 'STU':
        user_perm = this_petition.stu_permission
    elif user_type =='FAC':
        user_perm = this_petition.faculty_permission
    else:
        user_perm = this_petition.staff_permission

    sign_status = Sign.objects.filter(userID=user_info, petitionID=this_petition).exists()
    isOwner = this_petition.userID == user_info

    if (request.GET>get('delete_btn')):
        this_petition.delete()
        return redirect('/home')

    if (request.GET.get('sign_btn')):
        signature = Sign()
        signature.userID = user_info
        signature.petitionID = this_petition
        signature.time = datetime.datetime.now()
        signature.save()
        return redirect(this_petition.get_url())
    elif (request.GET.get('revoke_btn')):
        signature = Sign.objects.get(userID=user_info,petitionID=this_petition)
        if (signature != None):
            signature.delete()
        return redirect(this_petition.get_url())

    petDict = {
       'petition' : this_petition, \
       'clauses' : pet_clauses, \
       'user_perm' : int(user_perm), \
       'sign_status': sign_status, \
       'is_owner' :
    }
    return render(request,'view_petition.html',petDict)

@login_required
#Grab Petitions
def get_user_petitions(request):
    user_info = request.user.UserInfo
    myPetL = Petition.objects.filter(userID=user_info.email)
    fwPetL = list(get_follow_petitions(request))

    petDict = {
        'user' : request.user, \
        'UserInfo' : user_info, \
        'my_petitions' : myPetL, \
        'followed_petitions' : fwPetL
    }
    return petDict

def get_follow_petitions(request):
    user_info = request.user.UserInfo
    signL = Sign.objects.filter(userID=user_info.email)
    commL = Comment.objects.filter(userID=user_info.email)
    propL = Change.objects.filter(userID=user_info.email)
    petSet = set([])
    for i in range(0,len(signL)):
        signObj = signL[i]
        signPet = signObj.petitionID

        #Check that this isn't user's petition
        if signPet.userID == user_info:
            pass
        else:
            petSet.add(signPet)

    for i in range(0,len(commL)):
        commObj = commL[i]
        commPet = commObj.petitionID

        #Check that this isn't user's petition
        if commPet.userID == user_info:
            pass
        else:
            petSet.add(commPet)

    for i in range(0,len(propL)):
        propObj = propL[i]
        propPet = propObj.petitionID

        #Check that this isn't user's petition
        if propPet.userID == user_info:
            pass
        else:
            petSet.add(propPet)

    return petSet

def display_petition(request, pid):
    petition = Petition.objects.filter(petitionID = pid)
    if len(petition) == 0:
        return HttpResponse("This petition doesn't exist.")
    elif petition[0].finalized:
        return HttpResponse(petition[0])
    else:
        return HttpResponse("Petition not finalized.")