# Generated by Django 5.1.3 on 2024-11-14 08:03

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields
import uuid
import vibes_auth.managers
import vibes_auth.models
import vibes_auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='UUID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('email', models.EmailField(help_text="user's email address", max_length=254, unique=True, verbose_name='email')),
                ('phone_number', models.CharField(blank=True, help_text="user's phone number", max_length=20, null=True, unique=True, validators=[vibes_auth.validators.validate_phone_number], verbose_name='phone number')),
                ('first_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='last name')),
                ('avatar', models.ImageField(blank=True, help_text="user's profile image", null=True, upload_to=vibes_auth.models.User.get_uuid_as_path, verbose_name='avatar')),
                ('is_verified', models.BooleanField(default=False, help_text="user's verification status", verbose_name='is verified')),
                ('is_active', models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='is active')),
                ('is_subscribed', models.BooleanField(default=False, help_text="user's newsletter subscription status", verbose_name='is subscibed')),
                ('activation_token', models.UUIDField(default=uuid.uuid4, verbose_name='activation token')),
                ('language', models.CharField(choices=[('en-us', 'American English'), ('en-gb', 'English'), ('ru-ru', 'Русский'), ('de-de', 'Deutsch'), ('it-it', 'Italiano'), ('es-es', 'Español'), ('nl-nl', 'Nederlands'), ('fr-fr', 'Français'), ('ro-ro', 'Română'), ('pl-pl', 'Polska'), ('cs-cz', 'Česky'), ('da-dk', 'Dansk')], default='en-GB', max_length=7)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('recently_viewed', models.ManyToManyField(blank=True, help_text="user's recently viewed products", to='core.product', verbose_name='recently viewed')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'swappable': 'AUTH_USER_MODEL',
            },
            managers=[
                ('objects', vibes_auth.managers.UserManager()),
            ],
        ),
    ]
