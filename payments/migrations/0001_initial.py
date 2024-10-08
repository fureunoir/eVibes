# Generated by Django 5.0.8 on 2024-08-31 01:58

import django_extensions.db.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='UUID')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('amount', models.FloatField(default=0)),
            ],
            options={
                'verbose_name': 'Balance',
                'verbose_name_plural': 'Balances',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='UUID')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('amount', models.FloatField()),
                ('currency', models.CharField(max_length=3)),
                ('payment_method', models.CharField(max_length=20)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
