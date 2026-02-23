-- Добавление времени начала и конца консультации.
--
-- PostgreSQL:
--   psql -U postgres -d Diplom -f schema_add_consultation_times.sql

-- Время начала и конца (NULL для старых записей)
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS start_time TIME;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS end_time TIME;
