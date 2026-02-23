# Migration: добавление completed_at в consultations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0003_consultation_start_end_time'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='consultation',
                    name='completed_at',
                    field=models.DateTimeField(blank=True, null=True, verbose_name='Завершена'),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE consultations ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;',
                    reverse_sql='ALTER TABLE consultations DROP COLUMN IF EXISTS completed_at;',
                ),
            ],
        ),
    ]
