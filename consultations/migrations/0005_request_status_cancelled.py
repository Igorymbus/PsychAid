# Migration: добавить статус «Отменено» в request_statuses (для отмены обращения до консультации)
from django.db import migrations


def add_cancelled_status(apps, schema_editor):
    # Таблица managed=False, вставка через raw SQL
    from django.db import connection
    with connection.cursor() as c:
        c.execute(
            "INSERT INTO request_statuses (name) SELECT 'cancelled' "
            "WHERE NOT EXISTS (SELECT 1 FROM request_statuses WHERE name = 'cancelled')"
        )


def remove_cancelled_status(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        c.execute("DELETE FROM request_statuses WHERE name = 'cancelled'")


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0004_consultation_completed_at'),
    ]

    operations = [
        migrations.RunPython(add_cancelled_status, remove_cancelled_status),
    ]
