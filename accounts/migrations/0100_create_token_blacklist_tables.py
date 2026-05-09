from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),  # Adjust to your latest migration
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Create token_blacklist tables if they don't exist
            CREATE TABLE IF NOT EXISTS token_blacklist_outstandingtoken (
                id BIGSERIAL PRIMARY KEY,
                jti VARCHAR(255) NOT NULL UNIQUE,
                token TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                user_id BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS token_blacklist_blacklistedtoken (
                id BIGSERIAL PRIMARY KEY,
                blacklisted_at TIMESTAMPTZ NOT NULL,
                token_id BIGINT NOT NULL UNIQUE REFERENCES token_blacklist_outstandingtoken(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_user_id_idx 
                ON token_blacklist_outstandingtoken(user_id);
            CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_jti_idx 
                ON token_blacklist_outstandingtoken(jti);
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS token_blacklist_blacklistedtoken CASCADE;
            DROP TABLE IF EXISTS token_blacklist_outstandingtoken CASCADE;
            """
        ),
    ]
