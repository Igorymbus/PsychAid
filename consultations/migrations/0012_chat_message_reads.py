from django.db import migrations


def create_chat_message_reads_table(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as c:
        if vendor == 'sqlite':
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_message_reads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    read_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        else:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_message_reads (
                    id SERIAL PRIMARY KEY,
                    message_id INTEGER NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        c.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_chat_message_reads_message_user "
            "ON chat_message_reads(message_id, user_id);"
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_chat_message_reads_user ON chat_message_reads(user_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_chat_message_reads_message ON chat_message_reads(message_id);")


def drop_chat_message_reads_table(apps, schema_editor):
    with schema_editor.connection.cursor() as c:
        c.execute("DROP TABLE IF EXISTS chat_message_reads;")


class Migration(migrations.Migration):
    dependencies = [
        ('consultations', '0011_student_psychologist_chat'),
    ]

    operations = [
        migrations.RunPython(create_chat_message_reads_table, drop_chat_message_reads_table),
    ]

