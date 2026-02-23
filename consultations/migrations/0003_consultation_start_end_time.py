# Migration: добавление start_time и end_time в consultations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0002_consultation_students_schema'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='consultation',
                    name='start_time',
                    field=models.TimeField(blank=True, null=True, verbose_name='Время начала'),
                ),
                migrations.AddField(
                    model_name='consultation',
                    name='end_time',
                    field=models.TimeField(blank=True, null=True, verbose_name='Время окончания'),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE consultations ADD COLUMN IF NOT EXISTS start_time TIME;',
                    reverse_sql='ALTER TABLE consultations DROP COLUMN IF EXISTS start_time;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE consultations ADD COLUMN IF NOT EXISTS end_time TIME;',
                    reverse_sql='ALTER TABLE consultations DROP COLUMN IF EXISTS end_time;',
                ),
            ],
        ),
    ]
