from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('token_blacklist', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS token_blacklist_outstandingtoken (
                id SERIAL PRIMARY KEY,
                jti uuid NOT NULL UNIQUE,
                token text NOT NULL,
                created_at timestamptz NOT NULL,
                expires_at timestamptz NOT NULL,
                user_id bigint NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS token_blacklist_blacklistedtoken (
                id SERIAL PRIMARY KEY,
                blacklisted_at timestamptz NOT NULL,
                token_id integer NOT NULL UNIQUE
            );
            
            CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_user_id_idx 
            ON token_blacklist_outstandingtoken (user_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS token_blacklist_blacklistedtoken; DROP TABLE IF EXISTS token_blacklist_outstandingtoken;"
        ),
    ]
