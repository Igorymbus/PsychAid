from django import forms

from config.input_validation import validate_cyrillic_name, validate_student_birth_date

from .models import Student


class StudentForm(forms.ModelForm):
    middle_name = forms.CharField(
        max_length=50,
        label='Отчество',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
    )

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'classroom', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'classroom': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Для нового учащегося отчество обязательно; для старых записей при редактировании допускаем пустое.
        self.fields['middle_name'].required = not bool(getattr(self.instance, 'pk', None))
        first_name = (getattr(self.instance, 'first_name', '') or '').strip()
        if first_name:
            parts = first_name.split(' ', 1)
            self.initial.setdefault('first_name', parts[0])
            if len(parts) > 1:
                self.initial.setdefault('middle_name', parts[1])

    def clean_first_name(self):
        return validate_cyrillic_name(self.cleaned_data.get('first_name'), 'Имя')

    def clean_last_name(self):
        return validate_cyrillic_name(self.cleaned_data.get('last_name'), 'Фамилия')

    def clean_middle_name(self):
        middle = (self.cleaned_data.get('middle_name') or '').strip()
        if not middle:
            if self.fields['middle_name'].required:
                raise forms.ValidationError('Отчество обязательно для заполнения.')
            return ''
        return validate_cyrillic_name(middle, 'Отчество')

    def clean_birth_date(self):
        return validate_student_birth_date(self.cleaned_data.get('birth_date'))

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        middle_name = cleaned_data.get('middle_name', '')
        if not first_name or not last_name:
            return cleaned_data

        full_first_name = f'{first_name.strip()} {middle_name.strip()}'.strip()
        qs = Student.objects.filter(
            first_name__iexact=full_first_name,
            last_name__iexact=last_name.strip(),
        )
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Учащийся с таким ФИО уже существует.')
        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=False)
        first_name = (self.cleaned_data.get('first_name') or '').strip()
        middle_name = (self.cleaned_data.get('middle_name') or '').strip()
        obj.first_name = f'{first_name} {middle_name}'.strip()
        if commit:
            obj.save()
        return obj
