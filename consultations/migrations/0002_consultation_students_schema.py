# Migration: создание таблицы consultation_students и изменение consultations.request_id (nullable)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                # Разрешить консультации без привязки к обращению (планирование)
                'ALTER TABLE consultations ALTER COLUMN request_id DROP NOT NULL;',
                # Таблица связи консультация — учащиеся
                """CREATE TABLE IF NOT EXISTS consultation_students (
                    id SERIAL PRIMARY KEY,
                    consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
                    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                    UNIQUE(consultation_id, student_id)
                );""",
                'CREATE INDEX IF NOT EXISTS idx_consultation_students_consultation ON consultation_students(consultation_id);',
                'CREATE INDEX IF NOT EXISTS idx_consultation_students_student ON consultation_students(student_id);',
                # Перенос данных из существующих консультаций
                """INSERT INTO consultation_students (consultation_id, student_id)
                SELECT c.id, r.student_id FROM consultations c
                JOIN requests r ON c.request_id = r.id
                ON CONFLICT (consultation_id, student_id) DO NOTHING;""",
            ],
            reverse_sql=['DROP TABLE IF EXISTS consultation_students CASCADE;'],
            state_operations=[],
        ),
    ]
