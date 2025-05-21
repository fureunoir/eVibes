from django.db import migrations, models
from django.db.models.functions import Lower


def forwards(apps, schema_editor):
    User = apps.get_model('vibes_auth', 'User')
    User.objects.all().update(language=Lower('language'))


def backwards(apps, schema_editor):
    User = apps.get_model('vibes_auth', 'User')
    for u in User.objects.all():
        parts = u.language.split('-', 1)
        if len(parts) == 2:
            u.language = f"{parts[0].lower()}-{parts[1].upper()}"
            u.save(update_fields=['language'])


class Migration(migrations.Migration):
    dependencies = [
        ('vibes_auth', '0002_blacklistedtoken_outstandingtoken'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),

        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.CharField(
                choices=[
                    ('en-gb', 'English (British)'),
                    ('ar-ar', 'العربية'),
                    ('cs-cz', 'Česky'),
                    ('da-dk', 'Dansk'),
                    ('de-de', 'Deutsch'),
                    ('en-us', 'English (American)'),
                    ('es-es', 'Español'),
                    ('fr-fr', 'Français'),
                    ('hi-in', 'हिंदी'),
                    ('it-it', 'Italiano'),
                    ('ja-jp', '日本語'),
                    ('kk-kz', 'Қазақ'),
                    ('nl-nl', 'Nederlands'),
                    ('pl-pl', 'Polska'),
                    ('pt-br', 'Português'),
                    ('ro-ro', 'Română'),
                    ('ru-ru', 'Русский'),
                    ('zh-hans', '简体中文'),
                ],
                default='en-gb',
                max_length=7,
            ),
        ),
    ]
