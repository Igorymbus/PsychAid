# Migration: таблица уведомлений учащегося (назначение консультации, смена статуса обращения)
from django.db import migrations


def create_notifications_table(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS student_notifications (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                kind VARCHAR(30) NOT NULL,
                consultation_id INTEGER REFERENCES consultations(id) ON DELETE SET NULL,
                request_id INTEGER REFERENCES requests(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_student_notifications_student ON student_notifications(student_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_student_notifications_created ON student_notifications(created_at DESC);")


def drop_notifications_table(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as c:
        c.execute("DROP TABLE IF EXISTS student_notifications CASCADE;")


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0008_consultation_cancelled_at'),
    ]

    operations = [
        migrations.RunPython(create_notifications_table, drop_notifications_table),
    ]
