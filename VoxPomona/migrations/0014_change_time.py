# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-29 23:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('VoxPomona', '0013_auto_20170429_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='change',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
