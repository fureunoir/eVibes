# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-24 12:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

import swapper

from ..conf import ALTERNATIVE_NAME_TYPES


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0005_add_foreignkeys_to_postalcode'),
        swapper.dependency('geo', 'City'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternativename',
            name='is_historic',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alternativename',
            name='kind',
            field=models.CharField(choices=ALTERNATIVE_NAME_TYPES, default='name', max_length=4),
        ),
        migrations.AlterField(
            model_name='alternativename',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='postalcode',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='postal_codes', to=swapper.get_model_name('geo', 'City')),
        ),
    ]
