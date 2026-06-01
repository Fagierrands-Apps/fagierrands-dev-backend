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
            
            # If profile has no plate_number (null or empty) but verification has driving_license_number
            if (not profile.plate_number or profile.plate_number.strip() == '') and verification.driving_license_number:
                profile.plate_number = verification.driving_license_number
                profile.save(update_fields=['plate_number'])
                updated_count += 1
                print(f"Updated rider {rider.id}: {verification.driving_license_number}")
        except Profile.DoesNotExist:
            print(f"No profile for rider {rider.id}")
            continue
        except AssistantVerification.DoesNotExist:
            print(f"No verification for rider {rider.id}")
            continue
        except Exception as e:
            print(f"Error for rider {rider.id}: {e}")
            continue
    
    print(f"Synced plate numbers for {updated_count} riders")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0101_merge_20260510_0755'),
    ]

    operations = [
        migrations.RunPython(sync_plate_numbers, migrations.RunPython.noop),
    ]
