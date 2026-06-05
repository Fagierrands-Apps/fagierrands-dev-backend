from django.db import migrations, models


def add_accuracy_field(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'locations_userlocation'
                      AND column_name = 'accuracy'
                ) THEN
                    ALTER TABLE "locations_userlocation"
                        ADD COLUMN "accuracy" double precision NULL;
                END IF;
            END $$;
        """)
    elif schema_editor.connection.vendor == 'sqlite':
        try:
            schema_editor.execute('ALTER TABLE "locations_userlocation" ADD COLUMN "accuracy" REAL NULL;')
        except:
            pass  # Column might already exist


def add_heading_field(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'locations_userlocation'
                      AND column_name = 'heading'
                ) THEN
                    ALTER TABLE "locations_userlocation"
                        ADD COLUMN "heading" double precision NULL;
                END IF;
            END $$;
        """)
    elif schema_editor.connection.vendor == 'sqlite':
        try:
            schema_editor.execute('ALTER TABLE "locations_userlocation" ADD COLUMN "heading" REAL NULL;')
        except:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_accuracy_field, migrations.RunPython.noop),
        migrations.RunPython(add_heading_field, migrations.RunPython.noop),
        migrations.CreateModel(
            name='Waypoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('sequence', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='waypoints', to='orders.order')),
            ],
            options={
                'ordering': ['sequence'],
            },
        ),
        migrations.CreateModel(
            name='RouteCalculation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance_km', models.FloatField()),
                ('duration_minutes', models.FloatField()),
                ('calculated_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='route_calculation', to='orders.order')),
            ],
        ),
    ]
