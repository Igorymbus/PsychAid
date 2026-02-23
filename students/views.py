"""
CRUD учащихся. Доступ: психолог, администратор. Учащийся — только просмотр своего профиля.
"""
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from users.decorators import AdminRequiredMixin, PsychologistRequiredMixin, StudentRequiredMixin
from .models import Student
from .forms import StudentForm
from consultations.models import Note, RequestNote


class StudentListView(PsychologistRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        qs = Student.objects.all().order_by('last_name', 'first_name')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(last_name__icontains=q)
                | Q(first_name__icontains=q)
                | Q(classroom__name__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_q'] = self.request.GET.get('q', '')
        return ctx


class StudentDetailView(PsychologistRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student = ctx['student']

        # Заметки психолога по обращениям учащегося.
        request_notes = (
            RequestNote.objects
            .filter(request__student_id=student.pk, user__role__name='psychologist')
            .select_related('user', 'request')
            .order_by('-created_at')
        )

        # Заметки психолога по консультациям учащегося (через обращение и/или M2M участников).
        consultation_notes = (
            Note.objects
            .filter(
                Q(consultation__request__student_id=student.pk) |
                Q(consultation__students__id=student.pk),
                user__role__name='psychologist',
            )
            .select_related('user', 'consultation')
            .distinct()
            .order_by('-created_at')
        )

        combined = []
        for n in request_notes:
            combined.append({
                'kind': 'request',
                'created_at': n.created_at,
                'text': n.text,
                'author': n.user,
                'request_id': n.request_id,
                'consultation_id': None,
            })
        for n in consultation_notes:
            combined.append({
                'kind': 'consultation',
                'created_at': n.created_at,
                'text': n.text,
                'author': n.user,
                'request_id': n.consultation.request_id if n.consultation_id else None,
                'consultation_id': n.consultation_id,
            })

        combined.sort(key=lambda x: x['created_at'] or 0, reverse=True)
        ctx['psychologist_notes'] = combined[:30]
        ctx['psychologist_notes_total'] = len(combined)
        return ctx


class StudentCreateView(AdminRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def form_valid(self, form):
        messages.success(self.request, 'Учащийся добавлен.')
        return super().form_valid(form)


class StudentUpdateView(AdminRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')
    context_object_name = 'student'

    def form_valid(self, form):
        messages.success(self.request, 'Данные учащегося обновлены.')
        return super().form_valid(form)


class StudentDeleteView(AdminRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:student_list')
    context_object_name = 'student'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Учащийся удалён.')
        return super().delete(request, *args, **kwargs)


class StudentMyProfileView(StudentRequiredMixin, TemplateView):
    """Просмотр учащимся своей карточки (только чтение)."""
    template_name = 'students/student_my_profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['student'] = getattr(self.request.user, 'student', None)
        ctx['has_profile'] = ctx['student'] is not None
        return ctx

    def get(self, request, *args, **kwargs):
        if not getattr(request.user, 'student_id', None):
            messages.error(request, 'Ваш аккаунт не привязан к карточке учащегося. Обратитесь к администратору.')
            return redirect('consultations:student_dashboard')
        return super().get(request, *args, **kwargs)
