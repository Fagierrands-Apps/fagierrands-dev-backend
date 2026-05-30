# Generated migration to sync plate numbers from verification to profile

from django.db import migrations


def sync_plate_numbers(apps, schema_editor):
    """Copy driving_license_number from verification to profile.plate_number for riders"""
    User = apps.get_model('accounts', 'User')
    Profile = apps.get_model('accounts', 'Profile')
    AssistantVerification = apps.get_model('accounts', 'AssistantVerification')
    
    riders = User.objects.filter(user_type='rider')
    updated_count = 0
    
    for rider in riders:
        try:
            profile = Profile.objects.get(user=rider)
            verification = AssistantVerification.objects.get(user=rider)
            
            # If profile has no plate_number but verification has driving_license_number
            if not profile.plate_number and verification.driving_license_number:
                profile.plate_number = verification.driving_license_number
                profile.save()
                updated_count += 1
        except (Profile.DoesNotExist, AssistantVerification.DoesNotExist):
            continue
    
    print(f"Synced plate numbers for {updated_count} riders")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0101_merge_20260510_0755'),
    ]

    operations = [
        migrations.RunPython(sync_plate_numbers, migrations.RunPython.noop),
    ]
