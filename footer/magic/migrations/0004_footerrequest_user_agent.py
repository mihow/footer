# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 08:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magic', '0003_auto_20170222_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='footerrequest',
            name='user_agent',
            field=models.CharField(blank=True, editable=False, max_length=1024, null=True),
        ),
    ]
