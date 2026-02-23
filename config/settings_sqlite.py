"""
Настройки с SQLite — для выполнения makemigrations без подключения к PostgreSQL.
Используйте, если при makemigrations возникает UnicodeDecodeError при подключении к PostgreSQL
(часто на Windows при несовпадении кодировок).

Запуск:
  python manage.py makemigrations --settings=config.settings_sqlite

Для работы приложения используйте обычные настройки (config.settings) и PostgreSQL.
"""
from .settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}
