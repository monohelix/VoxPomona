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

# User Registration
def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # User default
            user = User.objects.create_user(form.cleaned_data.get('email'),
                form.cleaned_data.get('email'), form.cleaned_data.get('password'))
            user.save()

            # Create UserInfo to retain other info
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

# Logout Out: Simply logs out user and redirects to login
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

            #Sign this petition if the user has sign permission
            user_type = user_info.user_type
            sign_perm = False
            if (user_type == "Student"):
                sign_perm = int(petition.stu_permission) >= 2
            elif (user_type == "Faculty"):
                sign_perm = int(petition.staff_permission) >= 2
            else:
                sign_perm = int(petition.faculty_permission) >= 2

            if (sign_perm):
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
    pet_clauses = Clause.objects.filter(petitionID=this_petition).order_by('index')
    user_type = request.user.UserInfo.user_type

    if this_petition.finalized:
        return redirect(this_petition.get_url())

    if user_type == 'STU':
        user_perm = this_petition.stu_permission
    elif user_type =='FAC':
        user_perm = this_petition.faculty_permission
    else:
        user_perm = this_petition.staff_permission

    sign_status = Sign.objects.filter(userID=user_info, petitionID=this_petition).exists()
    is_owner = this_petition.userID == user_info

    change_list = Change.objects.filter(clauseID__in=pet_clauses)
    comment_list = Comment.objects.filter(clauseID__in=pet_clauses).order_by('time')
    change_votes = {}
    for change in change_list:
        currVo =ChangeVote.objects.filter(changeID=change.changeID)
        change_votes[change.changeID] = currVo



    if (request.GET.get('delete_btn')):
        Sign.objects.filter(petitionID=this_petition).delete()
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
       'is_owner' : is_owner, \
       'comments' : comment_list, \
       'changes' : change_list, \
       'change_votes' : change_votes
    }

    if is_owner:
        if request.method == 'POST':
            new_clause_form = NewClauseForm(request.POST)
            if new_clause_form.is_valid():
                clause = Clause()
                clause.petitionID = this_petition
                clause.index = Clause.objects.filter(petitionID=this_petition).count()
                clause.content = new_clause_form.cleaned_data.get('content')
                clause.time = datetime.datetime.now()
                clause.save()
                return redirect(this_petition.get_url())
            else:
                petDict['new_clause_form'] = new_clause_form
                return render(request,'view_petition.html',petDict)
        else: 
            new_clause_form = NewClauseForm()
            petDict['new_clause_form'] = new_clause_form
            return render(request,'view_petition.html',petDict)

    return render(request,'view_petition.html',petDict)

@login_required
#Deletes a clause for a given petition, assuming ownership
def delete_clause(request):
    user_info = request.user.UserInfo
    pid = request.POST.get('petition_id')
    cid = request.POST.get('clause_id')

    this_petition = Petition.objects.get(petitionID=pid)
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    #Delete current clause, and reorder the remaining clauses
    this_clause = Clause.objects.get(clauseID=cid)
    this_clause.delete()

    clause_list = Clause.objects.filter(petitionID=pid).order_by('index')
    for i in range(0,len(clause_list)):
        clause_list[i].index = i
        clause_list[i].save()

    return redirect(this_petition.get_url())

@login_required
#adds a comment to a given petition, assuming has permission
def add_comment(request):
    user_info = request.user.UserInfo
    cid = request.POST.get('clause_id')
    pid = request.POST.get('petition_id')
    this_clause = Clause.objects.get(clauseID=cid)
    this_petition = Petition.objects.get(petitionID=pid)

    if this_petition.finalized:
        return redirect(this_petition.get_url())

    comment = Comment()
    comment.userID = user_info
    comment.clauseID = this_clause
    comment.content = request.POST.get('content')
    comment.time = datetime.datetime.now()
    comment.save()

    return redirect(this_petition.get_url())

@login_required
def delete_comment(request):
    user_info = request.user.UserInfo
    pid = request.POST.get('petition_id')

    commentID = request.POST.get('comment_id')
    this_petition = Petition.objects.get(petitionID=pid)

    if this_petition.finalized:
        return redirect(this_petition.get_url())

    #Delete current comment
    this_comment = Comment.objects.get(commentID=commentID)
    this_comment.delete()

    return redirect(this_petition.get_url())

@login_required
#Add a proposed change to a clause, assuming permission
def add_change(request):
    user_info = request.user.UserInfo
    cid = request.POST.get('clause_id')
    this_clause = Clause.objects.get(clauseID=cid)

    pid = request.POST.get('petition_id')
    this_petition = Petition.objects.get(petitionID=pid)
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    change = Change()
    change.userID = user_info
    change.clauseID = this_clause
    change.content = request.POST.get('content')
    change.save()

    return redirect(this_petition.get_url())

@login_required
#Accept a proposed change to a clause (delete if change is empty)
def accept_change(request):
    cid = request.POST.get('clause_id')
    chid = request.POST.get('change_id')
    pid = request.POST.get('petition_id')

    this_clause = Clause.objects.get(clauseID=cid)
    this_change = Change.objects.get(changeID=chid)
    this_petition = Petition.objects.get(petitionID=pid)

    if this_petition.finalized:
        return redirect(this_petition.get_url())

    if (this_change.content == ''):
        this_change.delete()
        delete_clause(request)
    else:
        this_clause.content = this_change.content
        this_clause.time = datetime.datetime.now()
        this_clause.save()
        this_change.delete()
    return redirect(this_petition.get_url())

@login_required
#Reject a proposed change to a clause; ie delete the change
def reject_change(request):
    chid = request.POST.get('change_id')
    pid = request.POST.get('petition_id')

    this_change = Change.objects.get(changeID=chid)
    this_petition = Petition.objects.get(petitionID=pid)

    if this_petition.finalized:
        return redirect(this_petition.get_url())

    this_change.delete()
    return redirect(this_petition.get_url())

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

    for comment in commL:
        clause = comment.clauseID
        commPet = clause.petitionID

        #Check that this isn't user's petition
        if commPet.userID == user_info:
            pass
        else:
            petSet.add(commPet)
    
    for change in propL:
        clause = change.clauseID
        propPet = clause.petitionID

        #Check that this isn't user's petition
        if propPet.userID == user_info:
            pass
        else:
            petSet.add(propPet)

    return petSet

def display_petition(request, pid):
    petition = Petition.objects.filter(petitionID = pid)
    pet_clauses = Clause.objects.filter(petitionID=pid).order_by('index')
    petDict = {
        'petition' : petition[0], \
        'clauses' : pet_clauses
    }
    if len(petition) == 0:
        return HttpResponse("This petition doesn't exist.")
    elif petition[0].finalized:
        return render(request, 'petition.html', petDict)
    else:
        return HttpResponse("Petition not finalized.")

@login_required
def search_results(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            petitionID = form.cleaned_data.get('petitionID')
            title = form.cleaned_data.get('title')
            keyword = form.cleaned_data.get('keyword')
            category = form.cleaned_data.get('category')

            petition = Petition.objects.all()
            if user or petitionID or title or keyword or category:
                #only search if the search form is not entirely empty
                if user:
                    users = UserInfo.objects.filter(name__icontains = user).values_list('email', flat = True)
                    petition = petition.filter(userID__in = users)
                if petitionID:
                    petition = petition.filter(petitionID = petitionID)
                if title:
                    petition = petition.filter(title__icontains = title)
                if keyword:
                    petition = petition.filter(summary__icontains = keyword)
                if category:
                    petition = petition.filter(category = category)
            return render(request,'search_results.html',{'search_results': petition})
        else:
            return HttpResponse("form not valid.")
    else:
        form = SearchForm()
        return render(request, 'search.html', {'form': form})

@login_required
#Finalize a petition
def finalize_petition(request):
    #Grab the petition, and finalize it
    petitionID = request.POST.get('petition_id')
    this_petition = Petition.objects.get(petitionID=petitionID)
    this_petition.finalized = True
    this_petition.save()

    #Remove all comments and changes, since we won't display them anymore
    #Votes are automatically deleted, thanks to model design
    clauses = Clause.objects.filter(petitionID=petitionID)
    for clause in clauses:
        Comment.objects.filter(clauseID=clause.clauseID).delete()
        Change.objects.filter(clauseID=clause.clauseID).delete()

    return redirect(this_petition.get_url())