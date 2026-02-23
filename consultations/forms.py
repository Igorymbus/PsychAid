from datetime import date, datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from config.input_validation import normalize_spaces
from students.models import Student
from users.models import User

from .models import Consultation, Request


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('student', 'source', 'status')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_student(self):
        value = self.cleaned_data.get('student')
        if not value:
            raise ValidationError('Необходимо выбрать учащегося.')
        return value

    def clean_source(self):
        value = self.cleaned_data.get('source')
        if not value:
            raise ValidationError('Необходимо выбрать источник обращения.')
        return value

    def clean_status(self):
        value = self.cleaned_data.get('status')
        if not value:
            raise ValidationError('Необходимо выбрать статус обращения.')
        return value


class MyRequestCreateForm(forms.Form):
    note = forms.CharField(
        label='Заметка к обращению',
        required=False,
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите кратко ситуацию, с которой хотите обратиться к психологу.',
            }
        ),
        help_text='Необязательно. Можно оставить пустым.',
    )

    def clean_note(self):
        value = normalize_spaces(self.cleaned_data.get('note'))
        if value and len(value) < 5:
            raise ValidationError('Заметка слишком короткая. Укажите не менее 5 символов или оставьте поле пустым.')
        return value


class ConsultationNoteForm(forms.Form):
    text = forms.CharField(
        label='Заметка психолога',
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Добавьте рабочую заметку по консультации.',
            }
        ),
    )

    def clean_text(self):
        value = normalize_spaces(self.cleaned_data.get('text'))
        if not value:
            raise ValidationError('Введите текст заметки.')
        if len(value) < 3:
            raise ValidationError('Заметка слишком короткая.')
        return value


class ConsultationForm(forms.ModelForm):
    WORKDAY_START = datetime.strptime('08:30', '%H:%M').time()
    WORKDAY_END = datetime.strptime('16:00', '%H:%M').time()

    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        label='Учащиеся',
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'form-select consultation-students-select', 'size': 6}),
        help_text='Выберите одного или нескольких учащихся. Можно удерживать Ctrl для множественного выбора.',
    )

    class Meta:
        model = Consultation
        fields = ('request', 'students', 'date', 'start_time', 'end_time', 'form', 'result')
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'form': forms.Select(attrs={'class': 'form-select'}),
            'result': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'request': 'Обращение (необязательно, для контекста)',
            'start_time': 'Время начала',
            'end_time': 'Время окончания',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = Student.objects.order_by('last_name', 'first_name')
        self.fields['request'].required = False
        self.fields['result'].required = False

        if self.instance and self.instance.pk:
            self.fields['students'].initial = list(self.instance.students.values_list('pk', flat=True))
            if not self.fields['students'].initial and self.instance.request_id:
                self.fields['students'].initial = [self.instance.request.student_id]
        else:
            self.fields.pop('result', None)
            if self.initial.get('request'):
                from django.forms import HiddenInput

                self.fields['request'].widget = HiddenInput()
                self.fields['students'].initial = [self.initial['request'].student_id]

    def clean_students(self):
        value = self.cleaned_data.get('students')
        if not value:
            raise ValidationError('Выберите хотя бы одного учащегося.')
        return value

    def clean_date(self):
        value = self.cleaned_data.get('date')
        if not value:
            raise ValidationError('Дата консультации обязательна для заполнения.')
        # При регистрации новой консультации запрещаем прошедшие даты.
        if not self.instance.pk and value < timezone.now().date():
            raise ValidationError('Нельзя зарегистрировать консультацию на прошедшую дату.')
        return value

    def clean_form(self):
        value = self.cleaned_data.get('form')
        if not value:
            raise ValidationError('Необходимо выбрать форму консультации (индивидуальная/групповая).')
        return value

    def clean_start_time(self):
        value = self.cleaned_data.get('start_time')
        if value and (value < self.WORKDAY_START or value > self.WORKDAY_END):
            raise ValidationError('Время начала должно быть в диапазоне с 08:30 до 16:00.')
        return value

    def clean_end_time(self):
        start = self.cleaned_data.get('start_time')
        end = self.cleaned_data.get('end_time')
        if end and (end < self.WORKDAY_START or end > self.WORKDAY_END):
            raise ValidationError('Время окончания должно быть в диапазоне с 08:30 до 16:00.')
        if start and end and end <= start:
            raise ValidationError('Время окончания должно быть позже времени начала.')
        if start and end:
            minutes = int((datetime.combine(date.today(), end) - datetime.combine(date.today(), start)).total_seconds() / 60)
            if minutes > 120:
                raise ValidationError('Длительность консультации не может превышать 2 часа.')
        return end

    def clean_result(self):
        value = self.cleaned_data.get('result')
        if value is None:
            return value
        value = normalize_spaces(value)
        if value and len(value) < 10:
            raise ValidationError('Результат консультации слишком короткий. Укажите не менее 10 символов.')
        return value

    def clean(self):
        data = super().clean()
        date_val = data.get('date')
        result_val = (data.get('result') or '').strip()
        start_val = data.get('start_time')
        end_val = data.get('end_time')
        students_val = data.get('students')
        form_type = data.get('form')

        # Критичное правило: индивидуальная консультация только для одного учащегося.
        if form_type and form_type.name == 'individual' and students_val and len(students_val) > 1:
            self.add_error('students', 'Для индивидуальной консультации можно выбрать только одного учащегося.')
        if form_type and form_type.name == 'group' and students_val and len(students_val) < 2:
            self.add_error('students', 'Для групповой консультации нужно выбрать минимум двух учащихся.')

        if not self.instance.pk and (not start_val or not end_val):
            if not start_val:
                self.add_error('start_time', 'Укажите время начала консультации.')
            if not end_val:
                self.add_error('end_time', 'Укажите время окончания консультации.')

        # Для новой консультации на сегодня нельзя указывать уже прошедшее время начала.
        if not self.instance.pk and date_val and start_val:
            now = timezone.now()
            if date_val == now.date() and start_val <= now.time().replace(second=0, microsecond=0):
                self.add_error('start_time', 'Нельзя зарегистрировать консультацию на прошедшее время.')

        if date_val and 'result' in self.fields:
            today = timezone.now().date()
            if date_val < today and not result_val:
                self.add_error('result', 'Для прошедшей консультации укажите результат.')

        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        start = self.cleaned_data.get('start_time')
        end = self.cleaned_data.get('end_time')
        result = self.cleaned_data.get('result')

        if result is not None:
            instance.result = normalize_spaces(result) or None

        if start and end:
            dt_start = datetime.combine(date.today(), start)
            dt_end = datetime.combine(date.today(), end)
            duration_min = int((dt_end - dt_start).total_seconds() / 60)
            instance.duration = max(1, min(120, duration_min))

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ChatMessageForm(forms.Form):
    text = forms.CharField(
        label='Сообщение',
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите сообщение...',
            }
        ),
    )

    def clean_text(self):
        value = normalize_spaces(self.cleaned_data.get('text'))
        if not value:
            raise ValidationError('Введите текст сообщения.')
        if len(value) < 2:
            raise ValidationError('Сообщение слишком короткое.')
        return value


class ConsultationPsychologistAssignForm(forms.Form):
    psychologist = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='Психолог',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        empty_label='Выберите психолога',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['psychologist'].queryset = User.objects.filter(
            role__name='psychologist',
            is_active=True,
        ).order_by('username')
