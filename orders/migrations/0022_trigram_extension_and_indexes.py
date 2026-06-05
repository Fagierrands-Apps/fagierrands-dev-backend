from django.db import migrations


def apply_pg_trgm(apps, schema_editor):
    """Apply PostgreSQL-specific operations only if using PostgreSQL"""
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(
            "DO $$\n"
            "BEGIN\n"
            "  BEGIN\n"
            "    EXECUTE 'CREATE EXTENSION IF NOT EXISTS pg_trgm';\n"
            "  EXCEPTION WHEN undefined_file THEN\n"
            "    NULL;\n"
            "  END;\n"
            "END;\n"
            "$$;"
        )
        schema_editor.execute(
            "DO $$\n"
            "BEGIN\n"
            "  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') THEN\n"
            "    IF NOT EXISTS (\n"
            "      SELECT 1 FROM pg_class c\n"
            "      JOIN pg_namespace n ON n.oid = c.relnamespace\n"
            "      WHERE c.relkind = 'i' AND c.relname = 'idx_title_trgm'\n"
            "    ) THEN\n"
            "      EXECUTE 'CREATE INDEX idx_title_trgm ON orders_order USING GIN (title gin_trgm_ops)';\n"
            "    END IF;\n"
            "  END IF;\n"
            "END;\n"
            "$$;"
        )


def reverse_pg_trgm(apps, schema_editor):
    """Reverse PostgreSQL-specific operations only if using PostgreSQL"""
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(
            "DO $$\n"
            "BEGIN\n"
            "  IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'idx_title_trgm') THEN\n"
            "    EXECUTE 'DROP INDEX IF EXISTS idx_title_trgm';\n"
            "  END IF;\n"
            "END;\n"
            "$$;"
        )
        schema_editor.execute(
            "DO $$\n"
            "BEGIN\n"
            "  BEGIN\n"
            "    EXECUTE 'DROP EXTENSION IF EXISTS pg_trgm';\n"
            "  EXCEPTION WHEN undefined_object THEN\n"
            "    NULL;\n"
            "  END;\n"
            "END;\n"
            "$$;"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0021_alter_ordertype_base_price_alter_ordertype_min_price_and_more"),
    ]

    operations = [
        migrations.RunPython(apply_pg_trgm, reverse_pg_trgm),
    ]
