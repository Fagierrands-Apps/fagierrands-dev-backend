# Force sync plate numbers from verification to profile

from django.db import migrations


def force_sync_plate_numbers(apps, schema_editor):
    """Force sync driving_license_number to plate_number for all assistants (riders)"""
    User = apps.get_model('accounts', 'User')
    Profile = apps.get_model('accounts', 'Profile')
    AssistantVerification = apps.get_model('accounts', 'AssistantVerification')
    
    # Assistants are the riders
    assistants = User.objects.filter(user_type='assistant')
    updated_count = 0
    
    for assistant in assistants:
        try:
            profile = Profile.objects.get(user=assistant)
            verification = AssistantVerification.objects.get(user=assistant)
            
            # Update if verification has driving_license_number
            if verification.driving_license_number:
                profile.plate_number = verification.driving_license_number
                profile.save(update_fields=['plate_number'])
                updated_count += 1
                print(f"✅ Updated assistant {assistant.username} (ID: {assistant.id}): {verification.driving_license_number}")
        except Profile.DoesNotExist:
            print(f"⚠️  No profile for assistant {assistant.username} (ID: {assistant.id})")
        except AssistantVerification.DoesNotExist:
            print(f"⚠️  No verification for assistant {assistant.username} (ID: {assistant.id})")
        except Exception as e:
            print(f"❌ Error for assistant {assistant.id}: {e}")
    
    print(f"\n✅ Synced plate numbers for {updated_count} assistants")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0102_sync_plate_numbers_from_verification'),
    ]

    operations = [
        migrations.RunPython(force_sync_plate_numbers, migrations.RunPython.noop),
    ]
