# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 03:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VoxPomona', '0003_delete_fuck_migrations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='change',
            old_name='clause',
            new_name='clauseID',
        ),
        migrations.RenameField(
            model_name='changevote',
            old_name='chid',
            new_name='changeID',
        ),
        migrations.RenameField(
            model_name='commentvote',
            old_name='cid',
            new_name='commentID',
        ),
        migrations.AlterUniqueTogether(
            name='change',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='changevote',
            unique_together=set([('userID', 'changeID')]),
        ),
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together=set([('userID', 'commentID')]),
        ),
    ]
