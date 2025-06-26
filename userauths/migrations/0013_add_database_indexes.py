# Generated manually for database optimization
# This migration adds optimized indexes for PostgreSQL for userauths app

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0012_remove_ip_address_from_userconsent'),
    ]

    operations = [
        # User model indexes
        migrations.RunSQL(
            sql=[
                # User основные индексы
                "CREATE INDEX IF NOT EXISTS idx_user_email_lower ON userauths_user(LOWER(email));",
                "CREATE INDEX IF NOT EXISTS idx_user_username ON userauths_user(username);",
                "CREATE INDEX IF NOT EXISTS idx_user_phone ON userauths_user(phone);",
                "CREATE INDEX IF NOT EXISTS idx_user_gender ON userauths_user(gender);",
                "CREATE INDEX IF NOT EXISTS idx_user_is_active ON userauths_user(is_active);",
                "CREATE INDEX IF NOT EXISTS idx_user_date_joined ON userauths_user(date_joined);",
                "CREATE INDEX IF NOT EXISTS idx_user_last_login ON userauths_user(last_login);",
                
                # Составные индексы для User
                "CREATE INDEX IF NOT EXISTS idx_user_active_email ON userauths_user(is_active, email);",
                "CREATE INDEX IF NOT EXISTS idx_user_gender_active ON userauths_user(gender, is_active);",
                
                # Profile indexes
                "CREATE INDEX IF NOT EXISTS idx_profile_verified ON userauths_profile(verified);",
                "CREATE INDEX IF NOT EXISTS idx_profile_date ON userauths_profile(date);",
                "CREATE INDEX IF NOT EXISTS idx_profile_country ON userauths_profile(country);",
                "CREATE INDEX IF NOT EXISTS idx_profile_city ON userauths_profile(city);",
                "CREATE INDEX IF NOT EXISTS idx_profile_gender ON userauths_profile(gender);",
                "CREATE INDEX IF NOT EXISTS idx_profile_wallet ON userauths_profile(wallet);",
                
                # Составные индексы для Profile
                "CREATE INDEX IF NOT EXISTS idx_profile_verified_country ON userauths_profile(verified, country);",
                "CREATE INDEX IF NOT EXISTS idx_profile_country_city ON userauths_profile(country, city);",
                
                # UserConsent indexes
                "CREATE INDEX IF NOT EXISTS idx_userconsent_consent_type ON userauths_userconsent(consent_type);",
                "CREATE INDEX IF NOT EXISTS idx_userconsent_given_at ON userauths_userconsent(given_at);",
                "CREATE INDEX IF NOT EXISTS idx_userconsent_is_active ON userauths_userconsent(is_active);",
                "CREATE INDEX IF NOT EXISTS idx_userconsent_withdrawn_at ON userauths_userconsent(withdrawn_at);",
                "CREATE INDEX IF NOT EXISTS idx_userconsent_document_version ON userauths_userconsent(document_version);",
                
                # Составные индексы для UserConsent
                "CREATE INDEX IF NOT EXISTS idx_userconsent_user_type ON userauths_userconsent(user_id, consent_type);",
                "CREATE INDEX IF NOT EXISTS idx_userconsent_active_type ON userauths_userconsent(is_active, consent_type);",
                "CREATE INDEX IF NOT EXISTS idx_userconsent_user_active ON userauths_userconsent(user_id, is_active);",
                "CREATE INDEX IF NOT EXISTS idx_userconsent_type_version ON userauths_userconsent(consent_type, document_version);",
                
                # Функциональные индексы для текстового поиска
                "CREATE INDEX IF NOT EXISTS idx_user_fullname_trgm ON userauths_user USING gin(full_name gin_trgm_ops);",
                "CREATE INDEX IF NOT EXISTS idx_profile_fullname_trgm ON userauths_profile USING gin(full_name gin_trgm_ops);",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS idx_user_email_lower;",
                "DROP INDEX IF EXISTS idx_user_username;",
                "DROP INDEX IF EXISTS idx_user_phone;",
                "DROP INDEX IF EXISTS idx_user_gender;",
                "DROP INDEX IF EXISTS idx_user_is_active;",
                "DROP INDEX IF EXISTS idx_user_date_joined;",
                "DROP INDEX IF EXISTS idx_user_last_login;",
                "DROP INDEX IF EXISTS idx_user_active_email;",
                "DROP INDEX IF EXISTS idx_user_gender_active;",
                "DROP INDEX IF EXISTS idx_profile_verified;",
                "DROP INDEX IF EXISTS idx_profile_date;",
                "DROP INDEX IF EXISTS idx_profile_country;",
                "DROP INDEX IF EXISTS idx_profile_city;",
                "DROP INDEX IF EXISTS idx_profile_gender;",
                "DROP INDEX IF EXISTS idx_profile_wallet;",
                "DROP INDEX IF EXISTS idx_profile_verified_country;",
                "DROP INDEX IF EXISTS idx_profile_country_city;",
                "DROP INDEX IF EXISTS idx_userconsent_consent_type;",
                "DROP INDEX IF EXISTS idx_userconsent_given_at;",
                "DROP INDEX IF EXISTS idx_userconsent_is_active;",
                "DROP INDEX IF EXISTS idx_userconsent_withdrawn_at;",
                "DROP INDEX IF EXISTS idx_userconsent_document_version;",
                "DROP INDEX IF EXISTS idx_userconsent_user_type;",
                "DROP INDEX IF EXISTS idx_userconsent_active_type;",
                "DROP INDEX IF EXISTS idx_userconsent_user_active;",
                "DROP INDEX IF EXISTS idx_userconsent_type_version;",
                "DROP INDEX IF EXISTS idx_user_fullname_trgm;",
                "DROP INDEX IF EXISTS idx_profile_fullname_trgm;",
            ]
        ),
    ] 