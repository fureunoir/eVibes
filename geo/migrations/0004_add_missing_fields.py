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
    ]
