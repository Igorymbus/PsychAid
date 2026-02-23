"""
Декораторы и миксины для контроля доступа по ролям (psychologist, admin).
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def role_required(*role_names):
    """Доступ только для указанных ролей (по имени: admin, psychologist, student)."""
    def decorator(view):
        @wraps(view)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role_name not in role_names:
                raise PermissionDenied('Недостаточно прав.')
            return view(request, *args, **kwargs)
        return _wrapped
    return decorator


psychologist_required = role_required('psychologist', 'admin')
admin_required = role_required('admin')


class PsychologistRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Доступ: психолог или админ."""
    def test_func(self):
        return self.request.user.role_name in ('psychologist', 'admin')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Доступ: админ или is_superuser."""
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role_name == 'admin'


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Доступ: только учащийся (роль student)."""
    def test_func(self):
        return self.request.user.role_name == 'student'
