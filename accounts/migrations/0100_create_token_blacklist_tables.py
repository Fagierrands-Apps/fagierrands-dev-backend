from django.db import migrations, connection


def create_token_blacklist_tables(apps, schema_editor):
    is_postgres = connection.vendor == 'postgresql'
    
    with connection.cursor() as cursor:
        if is_postgres:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_blacklist_outstandingtoken (
                    id BIGSERIAL PRIMARY KEY,
                    jti VARCHAR(255) NOT NULL UNIQUE,
                    token TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL,
                    user_id BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_blacklist_blacklistedtoken (
                    id BIGSERIAL PRIMARY KEY,
                    blacklisted_at TIMESTAMPTZ NOT NULL,
                    token_id BIGINT NOT NULL UNIQUE REFERENCES token_blacklist_outstandingtoken(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_user_id_idx 
                    ON token_blacklist_outstandingtoken(user_id);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_jti_idx 
                    ON token_blacklist_outstandingtoken(jti);
            """)
        else:
            # SQLite
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_blacklist_outstandingtoken (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jti VARCHAR(255) NOT NULL UNIQUE,
                    token TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    expires_at DATETIME NOT NULL,
                    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_blacklist_blacklistedtoken (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    blacklisted_at DATETIME NOT NULL,
                    token_id INTEGER NOT NULL UNIQUE REFERENCES token_blacklist_outstandingtoken(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_user_id_idx 
                    ON token_blacklist_outstandingtoken(user_id);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_jti_idx 
                    ON token_blacklist_outstandingtoken(jti);
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_token_blacklist_tables, migrations.RunPython.noop),
    ]
