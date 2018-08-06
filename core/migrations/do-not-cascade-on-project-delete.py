# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-02 15:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', 'delete_t'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instances', to='core.Project'),
        ),
        migrations.AlterField(
            model_name='volume',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='volumes', to='core.Project'),
        ),
    ]