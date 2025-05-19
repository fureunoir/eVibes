from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('geo', '0002_alter_address_api_response_alter_address_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='district',
            field=models.CharField(max_length=255, null=True, verbose_name='district'),
        ),
    ]
