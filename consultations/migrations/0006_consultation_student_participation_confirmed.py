# Migration: подтверждение участия в консультации (поле в consultation_students)
from django.db import migrations


def add_participation_confirmed_column(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        if connection.vendor == 'postgresql':
            c.execute(
                "ALTER TABLE consultation_students "
                "ADD COLUMN IF NOT EXISTS participation_confirmed_at TIMESTAMP NULL;"
            )
        else:
            # SQLite and others: try to add (may fail if column exists)
            try:
                c.execute(
                    "ALTER TABLE consultation_students "
                    "ADD COLUMN participation_confirmed_at datetime NULL;"
                )
            except Exception:
                pass


def remove_participation_confirmed_column(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        if connection.vendor == 'postgresql':
            c.execute(
                "ALTER TABLE consultation_students "
                "DROP COLUMN IF EXISTS participation_confirmed_at;"
            )
        else:
            # SQLite doesn't support DROP COLUMN easily; skip
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0005_request_status_cancelled'),
    ]

    operations = [
        migrations.RunPython(add_participation_confirmed_column, remove_participation_confirmed_column),
    ]
