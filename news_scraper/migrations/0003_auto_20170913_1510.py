# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-13 15:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news_scraper', '0002_auto_20170913_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detectedevent',
            name='source_id',
        ),
        migrations.RemoveField(
            model_name='detectedevent',
            name='source_type',
        ),
    ]