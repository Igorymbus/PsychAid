from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    CREATE TABLE IF NOT EXISTS user_security_phrases (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                        phrase_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """,
                    reverse_sql="DROP TABLE IF EXISTS user_security_phrases;",
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='UserSecurityPhrase',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('phrase_hash', models.CharField(max_length=255)),
                        ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                        ('user', models.OneToOneField(db_column='user_id', on_delete=models.deletion.CASCADE, related_name='security_phrase', to='users.user')),
                    ],
                    options={
                        'db_table': 'user_security_phrases',
                        'managed': False,
                    },
                ),
            ],
        ),
    ]
