import re
from datetime import date, timedelta

from django.core.exceptions import ValidationError


_CYRILLIC_NAME_RE = re.compile(r"^[А-ЯЁа-яё]+(?:[ -][А-ЯЁа-яё]+)*$")
_LATIN_RE = re.compile(r"[A-Za-z]")
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def normalize_spaces(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def validate_cyrillic_name(value, field_label, min_len=2, max_len=50):
    value = normalize_spaces(value)
    if not value:
        raise ValidationError(f"{field_label} обязательно для заполнения.")
    if len(value) < min_len:
        raise ValidationError(f"{field_label} должно содержать не менее {min_len} символов.")
    if len(value) > max_len:
        raise ValidationError(f"{field_label} не должно превышать {max_len} символов.")
    if _LATIN_RE.search(value):
        raise ValidationError(f"{field_label} должно быть введено на русском языке (кириллицей).")
    if not _CYRILLIC_NAME_RE.fullmatch(value):
        raise ValidationError(
            f"{field_label} может содержать только кириллицу, пробел и дефис (без цифр и спецсимволов)."
        )
    return value


def validate_username_format(value):
    value = normalize_spaces(value)
    if not value:
        raise ValidationError("Введите логин.")
    if len(value) < 3:
        raise ValidationError("Логин должен быть не короче 3 символов.")
    if len(value) > 50:
        raise ValidationError("Логин не должен превышать 50 символов.")
    if not _USERNAME_RE.fullmatch(value):
        raise ValidationError("Логин может содержать только латинские буквы, цифры, '.', '_' и '-'.")
    return value


def validate_student_birth_date(value, min_age=5, max_age=25):
    if not value:
        raise ValidationError("Дата рождения обязательна для заполнения.")
    today = date.today()
    if value > today:
        raise ValidationError("Дата рождения не может быть в будущем.")
    if value < today - timedelta(days=365 * max_age):
        raise ValidationError("Укажите корректную дату рождения учащегося.")
    if value > today - timedelta(days=365 * min_age):
        raise ValidationError("Укажите корректную дату рождения учащегося.")
    return value
