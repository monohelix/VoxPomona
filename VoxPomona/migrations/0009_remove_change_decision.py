# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-26 05:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VoxPomona', '0008_auto_20170425_2150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='change',
            name='decision',
        ),
    ]
