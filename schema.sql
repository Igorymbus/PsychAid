-- Схема БД Kursach3 (PostgreSQL)
-- Выполнить: psql -U postgres -d "Kursach3" -f schema.sql

-- ===============================
-- СПРАВОЧНИК РОЛЕЙ
-- ===============================
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

INSERT INTO roles (name) VALUES ('admin'), ('psychologist'), ('student')
ON CONFLICT (name) DO NOTHING;

-- ===============================
-- УЧИТЕЛЯ
-- ===============================
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    subject VARCHAR(50),
    email VARCHAR(50)
);

-- ===============================
-- КЛАССЫ
-- ===============================
CREATE TABLE IF NOT EXISTS classrooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(10) UNIQUE NOT NULL,
    teacher_id INTEGER REFERENCES teachers(id)
);

-- ===============================
-- УЧАЩИЕСЯ
-- ===============================
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    class_id INTEGER REFERENCES classrooms(id),
    birth_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- ПОЛЬЗОВАТЕЛИ (Django: + is_active, last_login, is_staff, is_superuser)
-- ===============================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    student_id INTEGER UNIQUE REFERENCES students(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP NULL,
    is_staff BOOLEAN DEFAULT false,
    is_superuser BOOLEAN DEFAULT false
);

-- ===============================
-- РОДИТЕЛИ
-- ===============================
CREATE TABLE IF NOT EXISTS parents (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(50)
);

-- ===============================
-- СТАТУСЫ ОБРАЩЕНИЙ
-- ===============================
CREATE TABLE IF NOT EXISTS request_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

INSERT INTO request_statuses (name) VALUES ('new'), ('in_progress'), ('completed')
ON CONFLICT (name) DO NOTHING;

-- ===============================
-- ОБРАЩЕНИЯ
-- ===============================
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    psychologist_id INTEGER REFERENCES users(id),
    source VARCHAR(20) CHECK (source IN ('student', 'parent', 'teacher')),
    status_id INTEGER REFERENCES request_statuses(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- ФОРМЫ КОНСУЛЬТАЦИЙ
-- ===============================
CREATE TABLE IF NOT EXISTS consultation_forms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

INSERT INTO consultation_forms (name) VALUES ('individual'), ('group')
ON CONFLICT (name) DO NOTHING;

-- ===============================
-- КОНСУЛЬТАЦИИ
-- ===============================
CREATE TABLE IF NOT EXISTS consultations (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    form_id INTEGER REFERENCES consultation_forms(id),
    date DATE NOT NULL,
    duration INTEGER NOT NULL,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- ЗАМЕТКИ
-- ===============================
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    consultation_id INTEGER REFERENCES consultations(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- ВЛОЖЕНИЯ
-- ===============================
CREATE TABLE IF NOT EXISTS attachments (
    id SERIAL PRIMARY KEY,
    consultation_id INTEGER REFERENCES consultations(id) ON DELETE CASCADE,
    file_path VARCHAR(255),
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- СОБЫТИЯ
-- ===============================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    date DATE NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id)
);

-- ===============================
-- ОТЧЕТЫ
-- ===============================
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_name VARCHAR(100),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_data JSONB
);

-- ===============================
-- ЛОГИ
-- ===============================
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100),
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- УВЕДОМЛЕНИЯ УЧАЩЕГОСЯ
-- ===============================
CREATE TABLE IF NOT EXISTS student_notifications (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    kind VARCHAR(30) NOT NULL,
    consultation_id INTEGER REFERENCES consultations(id) ON DELETE SET NULL,
    request_id INTEGER REFERENCES requests(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_student_notifications_student ON student_notifications(student_id);
CREATE INDEX IF NOT EXISTS idx_student_notifications_created ON student_notifications(created_at DESC);

-- ===============================
-- ЗАМЕТКИ К ОБРАЩЕНИЯМ
-- ===============================
CREATE TABLE IF NOT EXISTS request_notes (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_request_notes_request ON request_notes(request_id);
CREATE INDEX IF NOT EXISTS idx_request_notes_created ON request_notes(created_at DESC);

-- ===============================
-- ЛИЧНЫЕ ЧАТЫ УЧАЩИХСЯ С ПСИХОЛОГОМ
-- ===============================
CREATE TABLE IF NOT EXISTS student_psychologist_chats (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
    psychologist_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sp_chats_psychologist ON student_psychologist_chats(psychologist_id);
CREATE INDEX IF NOT EXISTS idx_sp_chats_updated ON student_psychologist_chats(updated_at DESC);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES student_psychologist_chats(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL
);
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat ON chat_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_read_at ON chat_messages(read_at);

-- ===============================
-- ПРОЦЕДУРЫ
-- ===============================
CREATE OR REPLACE PROCEDURE add_student(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_class_id INT,
    p_birth_date DATE
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO students (first_name, last_name, class_id, birth_date)
    VALUES (p_first_name, p_last_name, p_class_id, p_birth_date);
END;
$$;

CREATE OR REPLACE PROCEDURE add_consultation(
    p_request_id INT,
    p_form_id INT,
    p_date DATE,
    p_duration INT,
    p_result TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO consultations (request_id, form_id, date, duration, result)
    VALUES (p_request_id, p_form_id, p_date, p_duration, p_result);
END;
$$;

CREATE OR REPLACE PROCEDURE update_request_status(p_request_id INT, p_status_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE requests SET status_id = p_status_id WHERE id = p_request_id;
END;
$$;

-- ===============================
-- ФУНКЦИИ
-- ===============================
CREATE OR REPLACE FUNCTION get_student_fullname(p_student_id INT)
RETURNS VARCHAR LANGUAGE plpgsql AS $$
BEGIN
    RETURN (SELECT first_name || ' ' || last_name FROM students WHERE id = p_student_id);
END;
$$;

CREATE OR REPLACE FUNCTION count_consultations(p_student_id INT)
RETURNS INT LANGUAGE plpgsql AS $$
BEGIN
    RETURN (SELECT COUNT(c.id) FROM consultations c JOIN requests r ON c.request_id = r.id WHERE r.student_id = p_student_id);
END;
$$;

CREATE OR REPLACE FUNCTION count_new_requests()
RETURNS INT LANGUAGE plpgsql AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM requests r JOIN request_statuses s ON r.status_id = s.id WHERE s.name = 'new');
END;
$$;

-- ===============================
-- ТРИГГЕРЫ
-- ===============================
CREATE OR REPLACE FUNCTION trg_check_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.duration > 120 THEN
        RAISE EXCEPTION 'Consultation duration cannot exceed 120 minutes';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS check_duration ON consultations;
CREATE TRIGGER check_duration
BEFORE INSERT OR UPDATE ON consultations
FOR EACH ROW EXECUTE FUNCTION trg_check_duration();

CREATE OR REPLACE FUNCTION trg_update_request_status()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE requests SET status_id = (SELECT id FROM request_statuses WHERE name = 'in_progress') WHERE id = NEW.request_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_request_status_after_consultation ON consultations;
CREATE TRIGGER update_request_status_after_consultation
AFTER INSERT ON consultations
FOR EACH ROW EXECUTE FUNCTION trg_update_request_status();

CREATE OR REPLACE FUNCTION trg_log_consultation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs(action) VALUES ('Consultation added');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS log_consultation ON consultations;
CREATE TRIGGER log_consultation
AFTER INSERT ON consultations
FOR EACH ROW EXECUTE FUNCTION trg_log_consultation();

-- ===============================
-- ПРЕДСТАВЛЕНИЯ
-- ===============================
CREATE OR REPLACE VIEW view_consultations AS
SELECT c.id, s.first_name, s.last_name, cl.name AS class_name, c.date, f.name AS form, c.duration, c.result
FROM consultations c
JOIN requests r ON c.request_id = r.id
JOIN students s ON r.student_id = s.id
LEFT JOIN classrooms cl ON s.class_id = cl.id
LEFT JOIN consultation_forms f ON c.form_id = f.id;

CREATE OR REPLACE VIEW view_consultation_counts AS
SELECT s.id, s.first_name, s.last_name, COUNT(c.id) AS total_consultations
FROM students s
LEFT JOIN requests r ON r.student_id = s.id
LEFT JOIN consultations c ON c.request_id = r.id
GROUP BY s.id, s.first_name, s.last_name;

CREATE OR REPLACE VIEW view_new_requests AS
SELECT r.id, s.first_name, s.last_name, r.created_at
FROM requests r
JOIN students s ON r.student_id = s.id
JOIN request_statuses st ON r.status_id = st.id
WHERE st.name = 'new';
