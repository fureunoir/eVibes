# core/migrations/0020_order_billing_address_order_shipping_address.py

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0019_address'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE core_order "
                "DROP COLUMN IF EXISTS billing_address_id, "
                "DROP COLUMN IF EXISTS shipping_address_id;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.AddField(
            model_name='order',
            name='billing_address',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.deletion.CASCADE,
                related_name='billing_address_order',
                to='core.address',
                verbose_name='billing address',
                help_text='the billing address used for this order',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.deletion.CASCADE,
                related_name='shipping_address_order',
                to='core.address',
                verbose_name='shipping address',
                help_text='the shipping address used for this order',
            ),
        ),
    ]
