-- Добавление поддержки нескольких учащихся в одной консультации
-- и планирования консультаций на будущее (request_id может быть NULL).
--
-- Выполнить в каталоге проекта:
--   psql -U postgres -d Diplom -f schema_add_consultation_students.sql

-- Разрешить консультации без привязки к обращению (планирование)
ALTER TABLE consultations ALTER COLUMN request_id DROP NOT NULL;

-- Таблица связи консультация — учащиеся (многие ко многим)
CREATE TABLE IF NOT EXISTS consultation_students (
    id SERIAL PRIMARY KEY,
    consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(consultation_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_consultation_students_consultation ON consultation_students(consultation_id);
CREATE INDEX IF NOT EXISTS idx_consultation_students_student ON consultation_students(student_id);

-- Перенос данных: учащиеся из существующих консультаций (через request)
INSERT INTO consultation_students (consultation_id, student_id)
SELECT c.id, r.student_id FROM consultations c
JOIN requests r ON c.request_id = r.id
ON CONFLICT (consultation_id, student_id) DO NOTHING;
