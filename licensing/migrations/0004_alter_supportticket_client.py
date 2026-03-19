from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('licensing', '0003_alter_order_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportticket',
            name='client',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='licensing.client',
            ),
        ),
    ]

