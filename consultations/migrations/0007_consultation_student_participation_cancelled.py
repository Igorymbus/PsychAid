# Migration: окончательная отмена участия (поле participation_cancelled_at)
from django.db import migrations


def add_column(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        if connection.vendor == 'postgresql':
            c.execute(
                "ALTER TABLE consultation_students "
                "ADD COLUMN IF NOT EXISTS participation_cancelled_at TIMESTAMP NULL;"
            )
        else:
            try:
                c.execute(
                    "ALTER TABLE consultation_students "
                    "ADD COLUMN participation_cancelled_at datetime NULL;"
                )
            except Exception:
                pass


def remove_column(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        if connection.vendor == 'postgresql':
            c.execute(
                "ALTER TABLE consultation_students "
                "DROP COLUMN IF EXISTS participation_cancelled_at;"
            )


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0006_consultation_student_participation_confirmed'),
    ]

    operations = [
        migrations.RunPython(add_column, remove_column),
    ]
