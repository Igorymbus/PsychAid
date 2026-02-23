"""
Вход/выход и управление пользователями (для администратора).
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Case, Q, Value, When
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from students.models import Student

from .decorators import AdminRequiredMixin
from .forms import PasswordRecoveryByCodeWordForm, StudentRegistrationForm
from .models import Role, User, UserSecurityPhrase


def login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'role_name', None) == 'student':
            return redirect('consultations:student_dashboard')
        return redirect('students:student_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.role_name == 'student':
                return redirect('consultations:student_dashboard')
            return redirect('students:student_list')
        messages.error(request, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('users:login')


def register_student_view(request):
    """Регистрация учащегося: создаётся карточка учащегося и учётная запись."""
    if request.user.is_authenticated:
        if getattr(request.user, 'role_name', None) == 'student':
            return redirect('consultations:student_dashboard')
        return redirect('students:student_list')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student_role = Role.objects.filter(name='student').first()
            if not student_role:
                messages.error(request, 'Регистрация временно недоступна. Обратитесь к администратору.')
                return render(request, 'users/register.html', {'form': form})

            student = Student.objects.create(
                first_name=f"{form.cleaned_data['first_name'].strip()} {form.cleaned_data['middle_name'].strip()}",
                last_name=form.cleaned_data['last_name'].strip(),
                classroom=form.cleaned_data['classroom'],
                birth_date=form.cleaned_data['birth_date'],
            )
            user = User.objects.create_user(
                username=form.cleaned_data['username'].strip(),
                password=form.cleaned_data['password1'],
                role=student_role,
                student=student,
            )
            UserSecurityPhrase.objects.update_or_create(
                user_id=user.pk,
                defaults={'phrase_hash': make_password(form.cleaned_data['security_phrase'])},
            )
            messages.success(request, 'Регистрация прошла успешно. Войдите, используя свой логин и пароль.')
            return redirect('users:login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def password_recovery_view(request):
    """Восстановление пароля через кодовое слово."""
    if request.user.is_authenticated:
        if getattr(request.user, 'role_name', None) == 'student':
            return redirect('consultations:student_dashboard')
        return redirect('students:student_list')

    if request.method == 'POST':
        form = PasswordRecoveryByCodeWordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            security_phrase = form.cleaned_data['security_phrase']
            new_password = form.cleaned_data['new_password1']

            user = User.objects.filter(username__iexact=username).first()
            if not user:
                messages.error(request, 'Пользователь с таким логином не найден.')
                return render(request, 'users/password_recovery.html', {'form': form})

            phrase_obj = UserSecurityPhrase.objects.filter(user_id=user.pk).first()
            if not phrase_obj or not check_password(security_phrase, phrase_obj.phrase_hash):
                messages.error(request, 'Кодовое слово указано неверно.')
                return render(request, 'users/password_recovery.html', {'form': form})

            user.set_password(new_password)
            user.save(update_fields=['password'])
            messages.success(request, 'Пароль успешно изменён. Теперь вы можете войти в систему.')
            return redirect('users:login')
    else:
        form = PasswordRecoveryByCodeWordForm()

    return render(request, 'users/password_recovery.html', {'form': form})


# --- Администратор: управление пользователями ---

class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.all().order_by('username')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(username__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_q'] = self.request.GET.get('q', '')
        return ctx


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    template_name = 'users/user_form.html'
    form_class = None
    success_url = reverse_lazy('users:user_list')

    def get_form_class(self):
        from .forms import UserCreateForm
        return UserCreateForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'student' in form.fields:
            form.fields['student'].queryset = Student.objects.order_by('last_name', 'first_name')
            form.fields['student'].required = False
            form.fields['student'].empty_label = '— Не привязан'
        return form

    def form_valid(self, form):
        form.save()
        user = form.instance
        student = form.cleaned_data.get('student')
        User.objects.filter(pk=user.pk).update(student_id=student.pk if student else None)
        messages.success(self.request, f'Пользователь {user.username} создан.')
        return redirect(self.success_url)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    template_name = 'users/user_form.html'
    form_class = None
    success_url = reverse_lazy('users:user_list')
    context_object_name = 'user_obj'

    def get_form_class(self):
        from .forms import UserEditForm
        return UserEditForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'student' in form.fields:
            form.fields['student'].required = False
            form.fields['student'].empty_label = '— Не привязан'
            base_qs = Student.objects.order_by('last_name', 'first_name')
            instance = getattr(form, 'instance', None)
            if instance and getattr(instance, 'student_id', None):
                sid = instance.student_id
                form.fields['student'].queryset = Student.objects.order_by(
                    Case(When(pk=sid, then=Value(0)), default=Value(1)),
                    'last_name', 'first_name'
                )
            else:
                form.fields['student'].queryset = base_qs
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        user = form.save(commit=False)
        student = form.cleaned_data.get('student')
        user.student_id = student.pk if student else None
        user.save(update_fields=['username', 'role_id', 'student_id', 'is_active', 'is_staff', 'is_superuser'])
        User.objects.filter(pk=user.pk).update(student_id=user.student_id)
        messages.success(self.request, f'Пользователь {user.username} обновлён.')
        return redirect(self.success_url)


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:user_list')
    context_object_name = 'user_obj'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj == request.user:
            messages.error(request, 'Нельзя удалить самого себя.')
            return redirect(self.success_url)
        linked_student_id = getattr(obj, 'student_id', None)
        if linked_student_id:
            Student.objects.filter(pk=linked_student_id).delete()
        messages.success(request, f'Пользователь {obj.username} удалён.')
        return super().delete(request, *args, **kwargs)
