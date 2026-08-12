# Generated migration for hardened OTP security

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_user_is_available'),
    ]

    operations = [
        # 1. Make otp field nullable for backward compatibility
        migrations.AlterField(
            model_name='otpverification',
            name='otp',
            field=models.CharField(max_length=6, null=True, blank=True),
        ),
        # 2. Add new fields to OTPVerification
        migrations.AddField(
            model_name='otpverification',
            name='otp_hash',
            field=models.CharField(max_length=255, default=''),
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
            field=models.DateTimeField(null=True, blank=True),
        ),
        
        # 2. Add database index for performance
        migrations.AddIndex(
            model_name='otpverification',
            index=models.Index(fields=['phone_number', '-created_at'], name='otpverif_phone_created_idx'),
        ),
        
        # 3. Remove old otp field (after migrating data)
        # Note: In production, you'd want to migrate otp values to otp_hash first
        # For now we keep it for backward compatibility and remove it in next migration
    ]
