from django.contrib import admin
from .models import UserInfo, Petition, Clause, Change, Comment, Sign, ChangeVote, CommentVote

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(Petition)
admin.site.register(Clause)
admin.site.register(Change)
admin.site.register(Comment)
admin.site.register(Sign)
admin.site.register(ChangeVote)
admin.site.register(CommentVote)