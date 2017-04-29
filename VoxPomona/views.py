from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
import operator

from datetime import datetime

from VoxPomona.forms import *
from VoxPomona.models import *


def register_view(request):
    '''
    User Registration - creates a basic user and a UserInfo for the database,
    and then redirects to the profile page. Uses the SignUpForm from forms.py
    '''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():

            # get the email, and check if it is a pomona email, non-pomona emails rejected
            email = form.cleaned_data.get('email')

            # create django built-in user object
            user = User.objects.create_user(email,
                email, form.cleaned_data.get('password'))
            user.save()

            # create UserInfo, which stores the info we will care about/use
            user_info = UserInfo()
            user_info.email = email
            user_info.name = form.cleaned_data.get('name')
            user_info.user_type = form.cleaned_data.get('user_type')
            user_info.user = user
            user_info.save()

            # redirect to the profile page:
            user = authenticate(username=email, password=request.POST.get('password'))
            if user is not None:
                if user.is_active:
                    login(request, user)
            return redirect('/profile')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

@login_required
def logout_view(request):
    '''Basic logout view that redirects to the login page'''
    logout(request)
    return redirect('login')

@login_required
def user_profile(request):
    '''Profile Page'''
    return render(request, 'profile.html')

@login_required
def home(request):
    ''' Home Page '''
    # grab a dictionary of current user-relevant info
    home_info = get_user_petitions(request)
    return render(request, 'home.html', home_info)

@login_required
def new_petition_view(request):
    '''
    Code to create a new petition. If user has permission, the user
    will automatically sign the petition. Uses the NewPetitionForm
    found in forms.py
    '''
    if request.method == 'POST':
        form = NewPetitionForm(request.POST)
        if form.is_valid():
            user_info = request.user.UserInfo

            # create New Form
            petition = Petition()
            petition.userID = user_info
            petition.title = form.cleaned_data.get('title')
            petition.summary = form.cleaned_data.get('summary')
            petition.category = form.cleaned_data.get('category')
            petition.stu_permission = form.cleaned_data.get('stu_permission')
            petition.staff_permission = form.cleaned_data.get('staff_permission')
            petition.faculty_permission = form.cleaned_data.get('faculty_permission')
            petition.finalized = False #By default, the petition is not final

            petition.open_time = datetime.now()
            petition.last_updated = datetime.now()
            petition.threshold = 10

            petition.save()

            # check if the user has sign permission
            user_type = user_info.user_type
            sign_perm = False
            if (user_type == "Student"):
                sign_perm = int(petition.stu_permission) >= 2
            elif (user_type == "Faculty"):
                sign_perm = int(petition.staff_permission) >= 2
            else:
                sign_perm = int(petition.faculty_permission) >= 2

            # if user has permission, sign the petition
            if (sign_perm):
                signature = Sign()
                signature.userID = user_info
                signature.petitionID = petition
                signature.time = datetime.now()
                signature.save()
            
            #redirect to the petition page
            return redirect(petition.get_url())
        else:
            return render(request, 'new_petition.html', {'form': form})
    else:
        form = NewPetitionForm()
        return render(request, 'new_petition.html', {'form': form})

@login_required
def view_petition_view(request,pid):
    '''
    The view for a petition, displaying all functions such as
    (for owners): adding/deleting/modifying clauses, finalizing, signing
    (none owners): adding comments, proposing changes - assuming permissions 
    '''

    # grab the user and petition id
    user_info = request.user.UserInfo
    this_petition = Petition.objects.get(petitionID=pid)

    # if the petition is finalized, it cannot be edited - redirect
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # check the permission of this user
    user_type = user_info.user_type
    if user_type == 'STU':
        user_perm = this_petition.stu_permission
    elif user_type =='FAC':
        user_perm = this_petition.faculty_permission
    else:
        user_perm = this_petition.staff_permission

    # check owner status and whether user has a signature on the petition
    is_owner = this_petition.userID == user_info
    if Sign.objects.filter(userID=user_info, petitionID=this_petition):
        sign_status = True
    else:
        sign_status = False

    # grab the clauses, proposed changes, comments, and votes for this petition
    pet_clauses = Clause.objects.filter(petitionID=this_petition).order_by('index')
    change_list = Change.objects.filter(clauseID__in=pet_clauses)
    comment_list = Comment.objects.filter(clauseID__in=pet_clauses).order_by('time')
    change_votes = {}
    for change in change_list:
        currVo =ChangeVote.objects.filter(changeID=change.changeID)
        change_votes[change.changeID] = currVo


    # button response for deleting a petition
    if (request.GET.get('delete_btn')):
        Sign.objects.filter(petitionID=this_petition).delete()
        this_petition.delete()
        return redirect('/home')

    # button responses for signing and revoking signature
    if (request.GET.get('sign_btn')):
        signature = Sign()
        signature.userID = user_info
        signature.petitionID = this_petition
        signature.time = datetime.now()
        signature.save()

        email_notification(this_petition,'S')
        return redirect(this_petition.get_url())
    elif (request.GET.get('revoke_btn')):
        Sign.objects.filter(userID=user_info,petitionID=this_petition).delete()
        email_notification(this_petition,'R')
        return redirect(this_petition.get_url())

    # create a dictionary that stores all the info the HTML file needs to render everything
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

    #if the user is an owner, NewClauseForm from forms.py for creating clauses
    if is_owner:
        if request.method == 'POST':
            new_clause_form = NewClauseForm(request.POST)
            if new_clause_form.is_valid():
                # generate a new clause upon interaction
                clause = Clause()
                clause.petitionID = this_petition
                clause.index = Clause.objects.filter(petitionID=this_petition).count()
                clause.content = new_clause_form.cleaned_data.get('content')
                clause.time = datetime.now()
                clause.save()

                # a new clause means to update the petition time 
                this_petition.last_updated = datetime.now()
                this_petition.save()

                # notify via email to all signators of change and redirect
                email_notification(this_petition,'L')
                return redirect(this_petition.get_url())
            else:
                petDict['new_clause_form'] = new_clause_form
                return render(request,'view_petition.html',petDict)
        else: 
            new_clause_form = NewClauseForm()
            petDict['new_clause_form'] = new_clause_form
            return render(request,'view_petition.html',petDict)

    # render the petition page
    return render(request,'view_petition.html',petDict)

@login_required
def delete_clause(request):
    '''
    Removes a clause, and its assocaited proposed changes, comments, and votes.
    Note that the database automatically deletes objects that depend on this
    clause due to the cascading flag used in models.py
    '''

    # grab basic info for quering from the page
    user_info = request.user.UserInfo
    pid = request.POST.get('petition_id')
    cid = request.POST.get('clause_id')

    # a finalized petition cannot be edited -- redirect 
    this_petition = Petition.objects.get(petitionID=pid)
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # delete current clause
    Clause.objects.filter(clauseID=cid).delete()

    # reorder the remaining clauses so we have proper ordering
    clause_list = Clause.objects.filter(petitionID=pid).order_by('index')
    for i in range(0,len(clause_list)):
        clause_list[i].index = i
        clause_list[i].save()

    # update the petition, notify signators, and refresh
    this_petition.last_updated = datetime.now()
    this_petition.save()
    email_notification(this_petition,'D')
    return redirect(this_petition.get_url())

@login_required
def add_comment(request):
    '''
    Assuming permission, add a comment to a clause; triggered
    via button click
    '''

    # get standard petition and user info
    user_info = request.user.UserInfo
    cid = request.POST.get('clause_id')
    pid = request.POST.get('petition_id')
    this_clause = Clause.objects.get(clauseID=cid)
    this_petition = Petition.objects.get(petitionID=pid)

    # a finalized petition cannot be modified -- redirect
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # create a new comment
    comment = Comment()
    comment.userID = user_info
    comment.clauseID = this_clause
    comment.content = request.POST.get('content')
    comment.time = datetime.now()
    comment.save()

    #notify owner of petition, refresh
    email_notification(this_petition,'C')
    return redirect(this_petition.get_url())

@login_required
def delete_comment(request):
    '''
    Removes a comment, assuming permission; also triggered
    via button press
    '''

    # get required info 
    user_info = request.user.UserInfo
    pid = request.POST.get('petition_id')
    commentID = request.POST.get('comment_id')
    this_petition = Petition.objects.get(petitionID=pid)

    # a finalized petition cannot have changes made to it -- redirect
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # delete current comment
    Comment.objects.filter(commentID=commentID).delete()

    # return to this page
    return redirect(this_petition.get_url())

@login_required
def add_change(request):
    '''
    Assuming permission, propose a change to a given clause
    '''

    # standard info grab
    user_info = request.user.UserInfo
    pid = request.POST.get('petition_id')
    cid = request.POST.get('clause_id')
    this_petition = Petition.objects.get(petitionID=pid)
    this_clause = Clause.objects.get(clauseID=cid)

    # finalized petitions cannot be modified 
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # add a proposed change to this clause
    change = Change()
    change.userID = user_info
    change.clauseID = this_clause
    change.content = request.POST.get('content')
    change.save()

    email_notification(this_petition,'P')
    return redirect(this_petition.get_url())

@login_required
def accept_change(request):
    '''
    Assuming petition ownership, accept a proposed change to
    a clause, either replacing the text with the change or 
    deleting the clause if the field is blank
    '''

    # grab info from page
    pid = request.POST.get('petition_id')
    cid = request.POST.get('clause_id')
    chid = request.POST.get('change_id')

    this_petition = Petition.objects.get(petitionID=pid)
    this_clause = Clause.objects.get(clauseID=cid)
    this_change = Change.objects.get(changeID=chid)

    # finalized petitions cannot be changed
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # delete the clause if the content is empty
    if (this_change.content == ''):
        this_change.delete()
        delete_clause(request)
    # otherwise adopt the change via overwriting
    else:
        this_clause.content = this_change.content
        this_clause.time = datetime.now()
        this_clause.save()
        this_change.delete()



    # update petition, notify owner redirect to page
    this_petition.last_updated = datetime.now()
    this_petition.save()
    email_notification(this_petition,'A')
    return redirect(this_petition.get_url())

@login_required
def reject_change(request):
    '''
    Assuming ownership, reject (delete) a proposed change
    '''

    # grab needed info
    chid = request.POST.get('change_id')
    pid = request.POST.get('petition_id')

    this_change = Change.objects.get(changeID=chid)
    this_petition = Petition.objects.get(petitionID=pid)

    # finalized petition cannot be changed
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    this_change.delete()

    # refresh page
    return redirect(this_petition.get_url())

@login_required
def get_user_petitions(request):
    '''
    For a given user, return a dict containing the user and user_info,
    petitions created by the user, and petitions that the user is
    following (signed, commented, or proposed changes)
    '''
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
    '''
    For a given user, grab the petitions that the user has signed,
    commented, or proposed changes. Returns a set.
    '''

    # grab from various models in which user has created
    user_info = request.user.UserInfo
    signL = Sign.objects.filter(userID=user_info.email)
    commL = Comment.objects.filter(userID=user_info.email)
    propL = Change.objects.filter(userID=user_info.email)

    # create a set to store all petitions, we don't want duplicates
    petSet = set([])

    # for each QuerySet, grab all petitions and store in set
    for sign in signL:
        signPet = sign.petitionID

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

    # return the set of petitions
    return petSet

def display_petition(request, pid):
    '''
    The display page for a finalized petition. Edits and modifications
    cannot be made, even by the owner.
    '''
    petition = Petition.objects.get(petitionID = pid)
    pet_clauses = Clause.objects.filter(petitionID=pid).order_by('index')
    petDict = {
        'petition' : petition, \
        'clauses' : pet_clauses
    }

    # check if petition exists
    if not petition:
        return HttpResponse("This petition doesn't exist.")
    elif petition.finalized:
        return render(request, 'petition.html', petDict)
    else:
        return HttpResponse("Petition not finalized.")

@login_required
def search_results(request):
    '''
    Search Query based on different criteria, suing the SearchForm()
    from forms.py
    '''
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # grab all the info from fields
            user = form.cleaned_data.get('user')
            petitionID = form.cleaned_data.get('petitionID')
            title = form.cleaned_data.get('title')
            keyword = form.cleaned_data.get('keyword')
            category = form.cleaned_data.get('category')
            open_time = form.cleaned_data.get('open_time')
            last_updated = form.cleaned_data.get('last_updated')

            petition = Petition.objects.all()
            if user or petitionID or title or keyword or category or open_time or last_updated:
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
                if open_time:
                    petition = petition.filter(open_time__gt = open_time)
                if last_updated:
                    petition = petition.filter(last_updated__gt = last_updated)
            byTime = sorted(petition, key = operator.attrgetter('last_updated'))
            return render(request,'search_results.html',{'search_results': petition})
        else:
            return HttpResponse("form not valid.")
    else:
        form = SearchForm()
        return render(request, 'search.html', {'form': form})

@login_required
def finalize_petition(request):
    '''
    Assuming ownership, finalize a petition via button press if allowable;
    (ie past 24 hours since last update and threshold reached)
    '''

    # grab petition info
    petitionID = request.POST.get('petition_id')
    this_petition = Petition.objects.get(petitionID=petitionID)

    # if finalizable conditions not met, reject and return to view
    if not(this_petition.finalizable()):
        redirect(this_petition.get_url())

    # finalize it
    this_petition.finalized = True
    this_petition.save()

    # remove all comments and changes, since we won't display them anymore
    # votes are automatically deleted, thanks to model design
    clauses = Clause.objects.filter(petitionID=petitionID)
    for clause in clauses:
        Comment.objects.filter(clauseID=clause.clauseID).delete()
        Change.objects.filter(clauseID=clause.clauseID).delete()

    # refresh the page, which should now redirect to page where petition
    # cant be modified
    return redirect(this_petition.get_url())

@login_required
def upvote_change(request):
    '''
    Upvote a proposed changed
    '''

    # standard info grab
    user_info = request.user.UserInfo
    pid = request.POST.get('petition_id')
    chid = request.POST.get('change_id')

    this_petition = Petition.objects.get(petitionID=pid)
    this_change = Change.objects.get(changeID=chid)

    # a finalized petition cannot have changes made to it -- redirect
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # check if user has already voted, and update the vote
    this_vote = ChangeVote.objects.filter(userID=user_info,changeID=this_change)
    if this_vote:
        this_vote[0].vote = True
        this_vote[0].save()
    # otherwise, create a new vote
    else:
        new_vote = ChangeVote()
        new_vote.userID = user_info
        new_vote.changeID = this_change
        new_vote.vote = True
        new_vote.save()

    # redirect to page after vote has been processed
    return redirect(this_petition.get_url())

@login_required
def downvote_change(request):
    '''
    Downvote a proposed changed
    '''

    # standard info grab
    user_info = request.user.UserInfo
    pid = request.POST.get('petition_id')
    chid = request.POST.get('change_id')

    this_petition = Petition.objects.get(petitionID=pid)
    this_change = Change.objects.get(changeID=chid)

    # a finalized petition cannot have changes made to it -- redirect
    if this_petition.finalized:
        return redirect(this_petition.get_url())

    # check if user has already voted, and update the vote
    this_vote = ChangeVote.objects.filter(userID=user_info,changeID=this_change)
    if this_vote:
        this_vote[0].vote = False
        this_vote[0].save()
    # otherwise, create a new vote
    else:
        new_vote = ChangeVote()
        new_vote.userID = user_info
        new_vote.changeID = this_change
        new_vote.vote = False
        new_vote.save()

    # redirect to page after vote has been processed
    return redirect(this_petition.get_url())

def email_notification(this_petition,messageType):
    '''
    Code for sending email notifications to owners or signators.
    Owners get notifications of new signators, revoked signators,
    comments, proposed changes, finalizable. Signators get
    notified of changes.

    MessageTypes: S: new sign               [Owner-specific]
                  R: revoked sign
                  C: comment
                  P: proposed change

                  N: new change proposed    [Signator-specific]
                  A: accepted change
                  L: new clause
                  D: deleted clause
    '''

    # grab some petition info needed for forming the email message
    owner = this_petition.userID
    title = this_petition.title
    url = this_petition.get_url()

    signs = Sign.objects.filter(petitionID=this_petition).order_by('-time')
    signators = signs.values_list('userID',flat=True)

    # owner specific email messages

    # 'S' = a new person has signed
    if messageType == 'S':
        latest_sign = signs[0]
        sign_count = signs.count()
        signator = latest_sign.userID

        message = ("Your petition: \"{title}\" has received a new signature by {person}!"
                   "This petition now has {count} signatures!"
                   "View your petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,person=signator,count=sign_count,url=url)
        send_mail('New Signature on Your Petition',message,'voxpomona@gmail.com',[owner.email])

    # 'R' = a signature has been revoked
    elif messageType == 'R':
        signs = Sign.objects.filter(petitionID=this_petition).order_by('-time')
        sign_count = signs.count()

        message = ("Your petition: \"{title}\" has lost a signature!"
                   "This petition now has {ccount} signatures."
                   "View your petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,count=sign_count,url=url)
        send_mail('Signature Revoked on Your Petition',message,'voxpomona@gmail.com',[owner.email])

    # 'C' = someone has commented on a clause
    elif messageType == 'C':
        clauses = Clause.objects.filter(petitionID=this_petition)
        comment = Comment.objects.filter(clauseID__in=clauses).order_by('-time')[0]
        commentor = comment.userID

        message = ("Your petition: \"{title}\" has received a comment by {person}."
                   "View your petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,person=commentor,url=url)
        send_mail('New Comment on Your Petition',message,'voxpomona@gmail.com',[owner.email])

    # 'P' = someone has proposed a change to a clause
    elif messageType == 'P':
        message = ("Your petition: \"{title}\" has received a proposed change"
                   "to one of its clauses."
                   "View your petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,url=url)
        send_mail('New Proposed Change on Your Petition',message,'voxpomona@gmail.com',[owner.email])

    # signator-specific messages

    # 'N' = a new change as been proposed to the signed petition
    elif messageType == 'N':
        proposer = change.userID

        message = ("The petition you signed: \"{title}\" has received a proposed change"
                   "to one of its clauses. View this petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,url=url)
        send_mail('New Proposed Change on a Petition You Signed',message,'voxpomona@gmail.com',signators)
    # 'A' = a new change has been accepted by the owner of the petition
    elif messageType == 'A':
        proposer = change.userID

        message = ("The owner of the petition: \"{title}\", which you signed, has accepted a new change"
                   "to one of its clauses. View this petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,url=url)
        send_mail('New Accepted Change on a Petition You Signed',message,'voxpomona@gmail.com',signators)

    # 'L' = the owner has added a new clause
    elif messageType == 'L':
        message = ("The owner of the petition: \"{title}\", which you signed, has added a new clause. "
                   "View this petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,url=url)
        send_mail('New Clause on a Petition You Signed',message,'voxpomona@gmail.com',signators)

    # 'D' = the owner has deleted a clause
    elif messageType == 'D':
        message = ("The owner of the petition: \"{title}\", which you signed, has deleted a clause. "
                   "View this petition at: \n"
                   "voxpomona.herokuapp.com{url}."
                   "\n\n-VoxPomona"
                  )
        message = message.format(title=title,url=url)
        send_mail('Deleted Clause on a Petition You Signed',message,'voxpomona@gmail.com',signators)
