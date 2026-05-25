# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0101_merge_20260510_0755'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bike_type',
            field=models.CharField(blank=True, help_text='Type of bike (e.g., Motorcycle, Bicycle)', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='bike_color',
            field=models.CharField(blank=True, help_text='Color of the bike', max_length=30, null=True),
        ),
    ]
