# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-21 13:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_scraper', '0002_auto_20170916_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='is_hot',
            field=models.BooleanField(default=False),
        ),
    ]