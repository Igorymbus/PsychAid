from django import forms
from django.core.exceptions import ValidationError

from config.input_validation import (
    normalize_spaces,
    validate_cyrillic_name,
    validate_student_birth_date,
    validate_username_format,
)
from students.models import Classroom, Student

from .models import User


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        min_length=8,
        error_messages={
            'required': 'Пароль обязателен для заполнения.',
            'min_length': 'Пароль должен содержать не менее 8 символов.',
        },
    )
    password2 = forms.CharField(
        label='Пароль (повтор)',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        error_messages={'required': 'Повторите пароль для подтверждения.'},
    )

    class Meta:
        model = User
        fields = ('username', 'role', 'student', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'student': 'Учащийся (привязка для роли «Учащийся»)',
            'role': 'Роль',
        }
        error_messages = {
            'username': {
                'required': 'Логин обязателен для заполнения.',
                'unique': 'Пользователь с таким логином уже существует.',
            },
            'role': {'required': 'Необходимо выбрать роль пользователя.'},
        }

    def clean_username(self):
        value = validate_username_format(self.cleaned_data.get('username'))
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return value

    def clean_role(self):
        value = self.cleaned_data.get('role')
        if not value:
            raise ValidationError('Необходимо выбрать роль пользователя.')
        return value

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise ValidationError('Повторите пароль для подтверждения.')
        if password1 != password2:
            raise ValidationError('Пароли не совпадают.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'role', 'student', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'student': 'Учащийся (привязка для роли «Учащийся»)',
            'role': 'Роль',
        }
        error_messages = {
            'username': {
                'required': 'Логин обязателен для заполнения.',
                'unique': 'Пользователь с таким логином уже существует.',
            },
            'role': {'required': 'Необходимо выбрать роль пользователя.'},
        }

    def clean_username(self):
        value = validate_username_format(self.cleaned_data.get('username'))
        qs = User.objects.filter(username__iexact=value)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return value

    def clean_role(self):
        value = self.cleaned_data.get('role')
        if not value:
            raise ValidationError('Необходимо выбрать роль пользователя.')
        return value


class StudentRegistrationForm(forms.Form):
    """Регистрация учащегося: ФИО, класс, дата рождения, логин и пароль."""

    first_name = forms.CharField(
        max_length=50,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}),
    )
    last_name = forms.CharField(
        max_length=50,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}),
    )
    middle_name = forms.CharField(
        max_length=50,
        label='Отчество',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванович'}),
    )
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.none(),
        label='Класс',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Укажите полную дату рождения.',
    )
    username = forms.CharField(
        max_length=50,
        label='Логин (для входа)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте логин'}),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label='Пароль (повтор)',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    security_phrase = forms.CharField(
        max_length=200,
        label='Кодовое слово',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',
                'placeholder': 'Введите кодовое слово для восстановления пароля',
            }
        ),
        help_text='Запомните это слово. Оно понадобится для восстановления пароля.',
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classroom'].queryset = Classroom.objects.all().order_by('name')

    def clean_first_name(self):
        return validate_cyrillic_name(self.cleaned_data.get('first_name'), 'Имя')

    def clean_last_name(self):
        return validate_cyrillic_name(self.cleaned_data.get('last_name'), 'Фамилия')

    def clean_middle_name(self):
        return validate_cyrillic_name(self.cleaned_data.get('middle_name'), 'Отчество')

    def clean_username(self):
        value = validate_username_format(self.cleaned_data.get('username'))
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError('Такой логин уже занят.')
        return value

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if not p2:
            raise ValidationError('Повторите пароль.')
        if p1 != p2:
            raise ValidationError('Пароли не совпадают.')
        return p2

    def clean_security_phrase(self):
        value = normalize_spaces(self.cleaned_data.get('security_phrase'))
        if not value:
            raise ValidationError('Введите кодовое слово.')
        if len(value) < 3:
            raise ValidationError('Кодовое слово слишком короткое.')
        return value

    def clean_birth_date(self):
        return validate_student_birth_date(self.cleaned_data.get('birth_date'))

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        middle_name = cleaned_data.get('middle_name')
        if not first_name or not last_name or not middle_name:
            return cleaned_data
        full_first_name = f'{first_name.strip()} {middle_name.strip()}'

        duplicate_exists = Student.objects.filter(
            first_name__iexact=full_first_name,
            last_name__iexact=last_name.strip(),
        ).exists()
        if duplicate_exists:
            raise ValidationError('Учащийся с таким ФИО уже существует.')
        return cleaned_data


class PasswordRecoveryByCodeWordForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш логин'}),
    )
    security_phrase = forms.CharField(
        max_length=200,
        label='Кодовое слово',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Кодовое слово'}),
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label='Новый пароль (повтор)',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

    def clean_username(self):
        return validate_username_format(self.cleaned_data.get('username'))

    def clean_security_phrase(self):
        value = normalize_spaces(self.cleaned_data.get('security_phrase'))
        if not value:
            raise ValidationError('Введите кодовое слово.')
        return value

    def clean_new_password2(self):
        p1 = self.cleaned_data.get('new_password1')
        p2 = self.cleaned_data.get('new_password2')
        if not p2:
            raise ValidationError('Повторите новый пароль.')
        if p1 != p2:
            raise ValidationError('Пароли не совпадают.')
        return p2
