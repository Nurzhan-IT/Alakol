# Generated manually to add pg_trgm extension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0095_auto_20250615_2332'),
    ]

    operations = [
        # Создание расширения pg_trgm для триграммного поиска
        migrations.RunSQL(
            sql=["CREATE EXTENSION IF NOT EXISTS pg_trgm;"],
            reverse_sql=["-- pg_trgm extension should not be dropped as it might be used elsewhere"],
        ),
    ] 