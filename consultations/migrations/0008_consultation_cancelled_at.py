# Migration: статус «Отменена» у консультации (cancelled_at)
from django.db import migrations


def add_cancelled_at(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        if connection.vendor == 'postgresql':
            c.execute(
                "ALTER TABLE consultations "
                "ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMP NULL;"
            )
        else:
            try:
                c.execute(
                    "ALTER TABLE consultations "
                    "ADD COLUMN cancelled_at datetime NULL;"
                )
            except Exception:
                pass


def remove_cancelled_at(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        if connection.vendor == 'postgresql':
            c.execute("ALTER TABLE consultations DROP COLUMN IF EXISTS cancelled_at;")


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0007_consultation_student_participation_cancelled'),
    ]

    operations = [
        migrations.RunPython(add_cancelled_at, remove_cancelled_at),
    ]
