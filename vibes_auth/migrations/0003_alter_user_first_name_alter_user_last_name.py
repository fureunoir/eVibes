# Generated by Django 5.0.8 on 2024-09-02 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vibes_auth', '0002_alter_user_activation_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='last name'),
        ),
    ]