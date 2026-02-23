from django.db import migrations


def create_request_notes_table(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as c:
        if vendor == 'sqlite':
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS request_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    text TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        else:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS request_notes (
                    id SERIAL PRIMARY KEY,
                    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        c.execute("CREATE INDEX IF NOT EXISTS idx_request_notes_request ON request_notes(request_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_request_notes_created ON request_notes(created_at DESC);")


def drop_request_notes_table(apps, schema_editor):
    with schema_editor.connection.cursor() as c:
        c.execute("DROP TABLE IF EXISTS request_notes;")


class Migration(migrations.Migration):
    dependencies = [
        ('consultations', '0009_student_notifications'),
    ]

    operations = [
        migrations.RunPython(create_request_notes_table, drop_request_notes_table),
    ]
