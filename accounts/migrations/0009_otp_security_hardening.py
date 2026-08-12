# Generated migration for OTP security hardening

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_user_is_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpverification',
            name='otp',
            field=models.CharField(default='', max_length=6, blank=True),
        ),
        migrations.AddField(
            model_name='otpverification',
            name='otp_hash',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='otpverification',
            name='attempt_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='otpverification',
            name='last_attempt_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='otpverification',
            name='purpose',
            field=models.CharField(
                choices=[
                    ('registration', 'Registration'),
                    ('password_reset', 'Password Reset'),
                    ('phone_verification', 'Phone Verification'),
                ],
                default='registration',
                max_length=30,
            ),
        ),
        migrations.AddIndex(
            model_name='otpverification',
            index=models.Index(fields=['phone_number', '-created_at'], name='accounts_ot_phone_n_idx'),
        ),
    ]
