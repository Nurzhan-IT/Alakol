# Generated manually for database optimization  
# This migration adds optimized indexes for PostgreSQL for legal app

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legal', '0002_remove_ip_address_from_documentview'),
    ]

    operations = [
        # LegalDocument and DocumentView indexes
        migrations.RunSQL(
            sql=[
                # LegalDocument основные индексы
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_document_type ON legal_legaldocument(document_type);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_version ON legal_legaldocument(version);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_is_active ON legal_legaldocument(is_active);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_language ON legal_legaldocument(language);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_effective_date ON legal_legaldocument(effective_date);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_created_at ON legal_legaldocument(created_at);",
                
                # Составные индексы для LegalDocument
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_type_active ON legal_legaldocument(document_type, is_active);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_type_language ON legal_legaldocument(document_type, language);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_active_language ON legal_legaldocument(is_active, language);",
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_type_version_lang ON legal_legaldocument(document_type, version, language);",
                
                # DocumentView indexes
                "CREATE INDEX IF NOT EXISTS idx_documentview_document_type ON legal_documentview(document_type);",
                "CREATE INDEX IF NOT EXISTS idx_documentview_viewed_at ON legal_documentview(viewed_at);",
                
                # Составные индексы для DocumentView
                "CREATE INDEX IF NOT EXISTS idx_documentview_user_type ON legal_documentview(user_id, document_type);",
                "CREATE INDEX IF NOT EXISTS idx_documentview_type_date ON legal_documentview(document_type, viewed_at);",
                "CREATE INDEX IF NOT EXISTS idx_documentview_user_date ON legal_documentview(user_id, viewed_at);",
                
                # Функциональные индексы для текстового поиска
                "CREATE INDEX IF NOT EXISTS idx_legaldocument_content_trgm ON legal_legaldocument USING gin(content gin_trgm_ops);",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS idx_legaldocument_document_type;",
                "DROP INDEX IF EXISTS idx_legaldocument_version;",
                "DROP INDEX IF EXISTS idx_legaldocument_is_active;",
                "DROP INDEX IF EXISTS idx_legaldocument_language;",
                "DROP INDEX IF EXISTS idx_legaldocument_effective_date;",
                "DROP INDEX IF EXISTS idx_legaldocument_created_at;",
                "DROP INDEX IF EXISTS idx_legaldocument_type_active;",
                "DROP INDEX IF EXISTS idx_legaldocument_type_language;",
                "DROP INDEX IF EXISTS idx_legaldocument_active_language;",
                "DROP INDEX IF EXISTS idx_legaldocument_type_version_lang;",
                "DROP INDEX IF EXISTS idx_documentview_document_type;",
                "DROP INDEX IF EXISTS idx_documentview_viewed_at;",
                "DROP INDEX IF EXISTS idx_documentview_user_type;",
                "DROP INDEX IF EXISTS idx_documentview_type_date;",
                "DROP INDEX IF EXISTS idx_documentview_user_date;",
                "DROP INDEX IF EXISTS idx_legaldocument_content_trgm;",
            ]
        ),
    ] 