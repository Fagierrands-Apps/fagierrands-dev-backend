from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_phone_number_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='account_manager',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='managed_clients',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='assistantverification',
            name='id_photo',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assistantverification',
            name='vehicle_photo',
            field=models.URLField(blank=True, null=True),
        ),
    ]
