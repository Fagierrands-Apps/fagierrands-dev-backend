# Generated manually for release code feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0043_reportissue'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='release_code',
            field=models.CharField(blank=True, help_text='6-digit code for order completion verification', max_length=6, null=True),
        ),
    ]
