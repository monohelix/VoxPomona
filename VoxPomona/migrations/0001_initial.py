# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 03:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('changeID', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.CharField(default='New Change', max_length=500)),
                ('decision', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ChangeVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.BooleanField()),
                ('chid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.Change')),
            ],
        ),
        migrations.CreateModel(
            name='Clause',
            fields=[
                ('clauseID', models.AutoField(primary_key=True, serialize=False)),
                ('index', models.IntegerField()),
                ('content', models.CharField(default='New Clause', max_length=500)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('commentID', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('clauseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.Clause')),
            ],
        ),
        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.BooleanField()),
                ('cid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='Petition',
            fields=[
                ('petitionID', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(choices=[('AC', 'Academics'), ('AA', 'Administrative Action'), ('CF', 'CF'), ('CP', 'CP'), ('DH', 'Dining Halls'), ('EA', 'Extracurricular Activities'), ('RH', 'Residence Halls'), ('OT', 'Other')], default='AC', max_length=2)),
                ('open_time', models.DateField()),
                ('close_time', models.DateField()),
                ('title', models.CharField(default='New Petition', max_length=50)),
                ('summary', models.CharField(default='A Petition', max_length=1000)),
                ('stu_permission', models.CharField(choices=[('1', 'view'), ('2', 'view, sign'), ('3', 'view, sign, comment'), ('4', 'view, sign, comment, propose changes'), ('5', 'view, sign, comment, propose changes, modify')], default=3, max_length=1)),
                ('staff_permission', models.CharField(choices=[('1', 'view'), ('2', 'view, sign'), ('3', 'view, sign, comment'), ('4', 'view, sign, comment, propose changes'), ('5', 'view, sign, comment, propose changes, modify')], default=3, max_length=1)),
                ('faculty_permission', models.CharField(choices=[('1', 'view'), ('2', 'view, sign'), ('3', 'view, sign, comment'), ('4', 'view, sign, comment, propose changes'), ('5', 'view, sign, comment, propose changes, modify')], default=3, max_length=1)),
                ('finalized', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Sign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('petitionID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.Petition')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('user_type', models.CharField(choices=[('STU', 'Student'), ('STA', 'Staff'), ('FAC', 'Faculty')], default='STU', max_length=3)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='UserInfo', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='sign',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.UserInfo', to_field='email'),
        ),
        migrations.AddField(
            model_name='petition',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.UserInfo', to_field='email'),
        ),
        migrations.AddField(
            model_name='commentvote',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.UserInfo', to_field='email'),
        ),
        migrations.AddField(
            model_name='comment',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.UserInfo', to_field='email'),
        ),
        migrations.AddField(
            model_name='clause',
            name='petitionID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.Petition'),
        ),
        migrations.AddField(
            model_name='changevote',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.UserInfo', to_field='email'),
        ),
        migrations.AddField(
            model_name='change',
            name='clause',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.Clause'),
        ),
        migrations.AddField(
            model_name='change',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoxPomona.UserInfo', to_field='email'),
        ),
        migrations.AlterUniqueTogether(
            name='sign',
            unique_together=set([('userID', 'petitionID')]),
        ),
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together=set([('userID', 'cid')]),
        ),
        migrations.AlterUniqueTogether(
            name='changevote',
            unique_together=set([('userID', 'chid')]),
        ),
        migrations.AlterUniqueTogether(
            name='change',
            unique_together=set([('userID', 'clause')]),
        ),
    ]
