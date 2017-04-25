from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

# plan to use Django user
# plan to use Django permission
class UserInfo(models.Model):
    email = models.EmailField(max_length = 100, unique = True)
    name = models.CharField(max_length = 100)
    USER_TYPE = (('STU','Student'), ('STA','Staff'),('FAC','Faculty'))
    user_type = models.CharField(max_length = 3, choices = USER_TYPE, default = 'STU')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name = "UserInfo", on_delete = models.CASCADE)

    def get_user_type(self):
        ty = self.user_type
        if ty == "STU":
            return "Student"
        elif ty == "STA":
            return "Staff"
        else:
            return "Faculty"

    def __unicode__(self):
        return (self.email)
    def __str__(self):
        return (self.email)

class Petition(models.Model):

    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete = models.CASCADE)
    # petitionID
    petitionID = models.AutoField(primary_key = True)

    # category
    ACADEMICS = 'AC'
    ADMINISTRATIVE_ACTION = 'AA'
    CAMPUS_FACILITIES = 'CF'
    COLLEGE_POLICY = 'CP'
    DINING_HALLS = 'DH'
    EXTRACURRICULAR_ACTIVITIES = 'EA'
    RESIDENCE_HALLS = 'RH'
    OTHER = 'OT'
    PETITION_CATEGORY_CHOICES = (
        (ACADEMICS,'Academics'),
        (ADMINISTRATIVE_ACTION, 'Administrative Action'),
        (CAMPUS_FACILITIES, 'CF'),
        (COLLEGE_POLICY, 'CP'),
        (DINING_HALLS, 'Dining Halls'),
        (EXTRACURRICULAR_ACTIVITIES, 'Extracurricular Activities'),
        (RESIDENCE_HALLS, 'Residence Halls'),
        (OTHER,'Other'),
        )
    category = models.CharField(
        max_length = 2,
        choices = PETITION_CATEGORY_CHOICES,
        # default = ACADEMICS,
        # blank = True
        )
    # open time
    open_time = models.DateField()
    # close time: no later than open_time
    close_time = models.DateField()
    # threshold: say = 10 for now
    threshold = 10
    title = models.CharField(max_length = 50, default = "New Petition")
    summary = models.CharField(max_length = 1000, default = "A Petition")
    # permissions
    PERM_CHOICES = (('1','view'),('2','view, sign'),('3','view, sign, comment'), 
        ('4','view, sign, comment, propose changes'),
        ('5','view, sign, comment, propose changes, modify'))
    stu_permission = models.CharField(max_length = 1, choices = PERM_CHOICES, default = 3)
    staff_permission = models.CharField(max_length = 1, choices = PERM_CHOICES, default = 3)
    faculty_permission = models.CharField(max_length = 1, choices = PERM_CHOICES, default = 3)
    finalized = models.BooleanField()

    def get_icon(self):
        cat = self.category
        if cat == 'AC':
            return 'school'
        elif cat == 'AA':
            return 'account_balance'
        elif cat == 'CF':
            return 'build'
        elif cat == 'CP':
            return 'gavel'
        elif cat == 'DH':
            return 'restaurant_menu'
        elif cat == 'EA':
            return 'directions_run'
        elif cat == 'RH':
            return 'hotel'
        else:
            return 'toc'

    def get_creator_name(self):
        creator = self.userID
        user = UserInfo.objects.get(email=creator)
        return user.name

    def get_url(self):
        return '/view_petition/' + str(self.petitionID)

    def get_signatures(self):
        return Sign.objects.filter(petitionID=self.petitionID)

    def __unicode__(self):
        return ("petition"+str(self.petitionID)+str(self.title))
    def __str__(self):
        return ("petition"+str(self.petitionID)+str(self.title))

class Clause(models.Model):
    clauseID = models.AutoField(primary_key=True)
    petitionID = models.ForeignKey(Petition, on_delete=models.CASCADE)
    index = models.IntegerField()
    content = models.CharField(max_length=500, default='New Clause')
    time = models.DateTimeField(auto_now_add=True) #what does the bool do?!

    def get_delete_btn_id(self):
        return str(self.index)

    def has_comments(self):
        if Comment.objects.filter(clauseID=self.clauseID):
            return True
        else:
            return False

    def __unicode__(self):
        return (str(self.petitionID)+" clause"+str(self.index))
    def __str__(self):
        return (str(self.petitionID)+" clause"+str(self.index))

class Change(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    clauseID = models.ForeignKey(Clause, to_field = 'clauseID', on_delete=models.CASCADE)
    changeID = models.AutoField(primary_key = True)
    content = models.CharField(max_length=500, default='New Change')
    decision = models.IntegerField() #limit this to 1, 2, 3
    def __unicode__(self):
        return ("change"+str(self.changeID))
    def __str__(self):
        return ("change"+str(self.changeID))

class Comment(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    clauseID = models.ForeignKey(Clause, to_field = 'clauseID', on_delete=models.CASCADE)
    commentID = models.AutoField(primary_key = True)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True, blank=True)

    def get_name(self):
        return UserInfo.objects.get(email=self.userID).name

    def __unicode__(self):
        return ("comment"+str(self.commentID))
    def __str__(self):
        return ("comment"+str(self.commentID))

class Sign(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    petitionID = models.ForeignKey(Petition) #on-delete???
    time = models.DateTimeField()

    def get_name(self):
        return UserInfo.objects.get(email=self.userID).name

    class Meta:
        unique_together = ("userID","petitionID")

class ChangeVote(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    changeID = models.ForeignKey(Change, to_field = 'changeID', on_delete=models.CASCADE)
    vote = models.BooleanField()
    class Meta:
        unique_together = ("userID","changeID")

class CommentVote(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    commentID = models.ForeignKey(Comment, to_field = 'commentID', on_delete=models.CASCADE)
    vote = models.BooleanField()
    class Meta:
        unique_together = ("userID","commentID")