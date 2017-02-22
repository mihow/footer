# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 08:03
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magic', '0002_auto_20170218_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='footerrequest',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='footerrequest',
            name='location',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='footerrequest',
            name='image',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to=b''),
        ),
        migrations.AlterField(
            model_name='footerrequest',
            name='is_leader',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='footerrequest',
            name='request_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, editable=False, null=True),
        ),
    ]
