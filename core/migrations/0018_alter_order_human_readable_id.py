from django.db.models import Count

import core.utils
from django.db import migrations, models


def fix_duplicates(apps, schema_editor):
    Order = apps.get_model("core", "Order")
    duplicates = (
        Order.objects.values("human_readable_id")
        .annotate(count=Count("uuid"))
        .filter(count__gt=1)
    )
    for duplicate in duplicates:
        h_id = duplicate["human_readable_id"]
        orders = Order.objects.filter(human_readable_id=h_id).order_by("uuid")
        for order in orders[1:]:
            new_id = order.human_readable_id
            while Order.objects.filter(human_readable_id=new_id).exists():
                from core.utils import generate_human_readable_id
                new_id = generate_human_readable_id()
            order.human_readable_id = new_id
            order.save()


def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_order_human_readable_id'),
    ]

    operations = [
        migrations.RunPython(fix_duplicates, reverse_func),
        migrations.AlterField(
            model_name='order',
            name='human_readable_id',
            field=models.CharField(default=core.utils.generate_human_readable_id, help_text='a human-readable identifier for the order', max_length=8, unique=True, verbose_name='human readable id'),
        ),
    ]
