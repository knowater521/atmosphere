# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-06 19:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', 'remove-old-allocation-models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atmosphereuser',
            name='selected_identity',
        ),
    ]
