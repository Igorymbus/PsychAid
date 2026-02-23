from django.db import migrations


def create_chat_tables(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as c:
        if vendor == 'sqlite':
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS student_psychologist_chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
                    psychologist_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL REFERENCES student_psychologist_chats(id) ON DELETE CASCADE,
                    author_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    text TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    read_at DATETIME NULL
                );
                """
            )
        else:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS student_psychologist_chats (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
                    psychologist_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    chat_id INTEGER NOT NULL REFERENCES student_psychologist_chats(id) ON DELETE CASCADE,
                    author_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP NULL
                );
                """
            )
        c.execute("CREATE INDEX IF NOT EXISTS idx_sp_chats_psychologist ON student_psychologist_chats(psychologist_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sp_chats_updated ON student_psychologist_chats(updated_at DESC);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_chat ON chat_messages(chat_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at DESC);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_read_at ON chat_messages(read_at);")


def drop_chat_tables(apps, schema_editor):
    with schema_editor.connection.cursor() as c:
        c.execute("DROP TABLE IF EXISTS chat_messages;")
        c.execute("DROP TABLE IF EXISTS student_psychologist_chats;")


class Migration(migrations.Migration):
    dependencies = [
        ('consultations', '0010_request_notes'),
    ]

    operations = [
        migrations.RunPython(create_chat_tables, drop_chat_tables),
    ]
