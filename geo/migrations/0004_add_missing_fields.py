import django.contrib.gis.db.models.fields
from django.conf import settings

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('geo', '0003_add_district_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=255, null=True, verbose_name='city'),
        ),
        migrations.AddField(
            model_name='address',
            name='region',
            field=models.CharField(max_length=255, null=True, verbose_name='region'),
        ),
        migrations.AddField(
            model_name='address',
            name='postal_code',
            field=models.CharField(max_length=255, null=True, verbose_name='postal_code'),
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.CharField(max_length=255, null=True, verbose_name='country'),
        ),
        migrations.AddField(
            model_name='address',
            name='location',
            field=django.contrib.gis.db.models.PointField(blank=True, geography=True,
                                                          help_text='Geolocation point: (longitude, latitude)',
                                                          null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='address',
            name='raw_data',
            field=models.JSONField(blank=True, help_text='Full JSON response from geocoder for this address',
                                   null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='api_response',
            field=models.JSONField(blank=True, help_text='Stored JSON response from the geocoding service', null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]
