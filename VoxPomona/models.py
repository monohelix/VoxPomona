# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

from datetime import datetime, timedelta

# implementation of the relational schema

class UserInfo(models.Model):
    # email of the user, used as primary key
    email = models.EmailField(max_length = 100, unique = True)
    # name that the user registered with
    name = models.CharField(max_length = 100)
    # user type, student, staff or faculty
    USER_TYPE = (('STU','Student'), ('STA','Staff'),('FAC','Faculty'))
    user_type = models.CharField(max_length = 3, choices = USER_TYPE, default = 'STU')
    # Django user 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name = "UserInfo", on_delete = models.CASCADE)

    # return the user type
    def get_user_type(self):
        ty = self.user_type
        if ty == "STU":
            return "Student"
        elif ty == "STA":
            return "Staff"
        else:
            return "Faculty"

    # for admin site display
    def __unicode__(self):
        return (self.email)
    def __str__(self):
        return (self.email)

class Petition(models.Model):

    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete = models.CASCADE)
    # auto filled petitionID
    petitionID = models.AutoField(primary_key = True)

    # category options
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
        (CAMPUS_FACILITIES, 'Campus Facilities'),
        (COLLEGE_POLICY, 'Campus Policy'),
        (DINING_HALLS, 'Dining Halls'),
        (EXTRACURRICULAR_ACTIVITIES, 'Extracurricular Activities'),
        (RESIDENCE_HALLS, 'Residence Halls'),
        (OTHER,'Other'),
        )
    category = models.CharField(
        max_length = 2,
        choices = PETITION_CATEGORY_CHOICES,
        # default = ACADEMICS,
        blank = True
        )
    # open time
    open_time = models.DateTimeField()
    last_updated = models.DateTimeField()
    # threshold: fixed to 10
    threshold = 10
    title = models.CharField(max_length = 100)
    summary = models.CharField(max_length = 1000)
    # permissions, has four different levels
    PERM_CHOICES = (('1','view'),('2','view, sign'),('3','view, sign, comment'), 
        ('4','view, sign, comment, propose changes'))
    stu_permission = models.CharField(max_length = 1, choices = PERM_CHOICES, default = 4)
    sta_permission = models.CharField(max_length = 1, choices = PERM_CHOICES, default = 4)
    fac_permission = models.CharField(max_length = 1, choices = PERM_CHOICES, default = 4)
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

    def get_creator_user_type(self):
        return self.userID.get_user_type()

    # if petition is finalized, return url to display the petition
    # otherwise give the url
    def get_url(self):
        if self.finalized:
            return '/petition/' + str(self.petitionID)
        return '/view_petition/' + str(self.petitionID)

    def get_edit_url(self):
        if self.finalized:
            return '/petition/' + str(self.petitionID)
        return '/edit_petition/' + str(self.petitionID)

    def get_signatures(self):
        return Sign.objects.filter(petitionID=self.petitionID)

    def get_clauses(self):
        return Clause.objects.filter(petitionID=self.petitionID).order_by('-time')

    def get_num_signatures_needed(self):
        sigs = self.get_signatures()
        if len(sigs) >= 10:
            return 0
        else:
            return 10 - len(sigs)

    def get_time_remaining(self):
        time = timezone.now() - timedelta(days=1)
        if self.last_updated <= time:
            return 0
        else:
            diff = self.last_updated - time
            return int(diff.seconds / 60 / 60)

    def is_finalizable(self):
        clauses = self.get_clauses()
        if len(clauses) == 0:
            return False

        if self.get_num_signatures_needed() > 0:
            return False

        time = timezone.now() - timedelta(days=1)
        if self.last_updated > time:
            return False
        return True

    def __unicode__(self):
        return ("petition"+str(self.petitionID)+self.title.encode('utf8'))
    def __str__(self):
        return ("petition"+str(self.petitionID)+self.title.encode('utf8'))

class Clause(models.Model):
    clauseID = models.AutoField(primary_key=True)
    petitionID = models.ForeignKey(Petition, on_delete=models.CASCADE)
    # index of the clause in the petition
    index = models.IntegerField()
    content = models.CharField(max_length=500, default='New Clause')
    # time that the clause was created
    time = models.DateTimeField(auto_now_add=True)

    # retrieves id for button
    def get_delete_btn_id(self):
        return str(self.index)

    def has_comments(self):
        if Comment.objects.filter(clauseID=self.clauseID):
            return True
        else:
            return False

    def has_changes(self):
        if Change.objects.filter(clauseID=self.clauseID):
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
    time = models.DateTimeField()

    def get_name(self):
        return self.userID.name

    def get_votes(self):
        netVotes = 0
        votes = ChangeVote.objects.filter(changeID=self.changeID)
        for v in votes:
            if v.vote:
                netVotes += 1
            else:
                netVotes -= 1
        return netVotes

    def __unicode__(self):
        return ("change"+str(self.changeID))
    def __str__(self):
        return ("change"+str(self.changeID))

class Comment(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    clauseID = models.ForeignKey(Clause, to_field = 'clauseID', on_delete=models.CASCADE)
    commentID = models.AutoField(primary_key = True)
    content = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True, blank=True)

    def get_name(self):
        return self.userID.name

    def __unicode__(self):
        return ("comment"+str(self.commentID))
    def __str__(self):
        return ("comment"+str(self.commentID))

class Sign(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    petitionID = models.ForeignKey(Petition) #on-delete???
    time = models.DateTimeField()

    def get_name(self):
        return self.userID.name

    def get_user_type(self):
        return self.userID.get_user_type()

    class Meta:
        unique_together = ("userID","petitionID")

class ChangeVote(models.Model):
    userID = models.ForeignKey(UserInfo, to_field = 'email', on_delete=models.CASCADE)
    changeID = models.ForeignKey(Change, to_field = 'changeID', on_delete=models.CASCADE)
    vote = models.BooleanField()
    class Meta:
        unique_together = ("userID","changeID")