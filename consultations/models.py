"""
Модели: request_statuses, requests, consultation_forms, consultations, notes, attachments, events, reports, logs.
managed=False — таблицы создаются schema.sql.
"""
from django.db import models
from django.conf import settings


class RequestStatus(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'request_statuses'
        managed = False

    def __str__(self):
        return {'new': 'Новое', 'in_progress': 'В работе', 'completed': 'Завершено', 'cancelled': 'Отменено'}.get(self.name, self.name)


class Request(models.Model):
    SOURCE_STUDENT = 'student'
    SOURCE_PARENT = 'parent'
    SOURCE_TEACHER = 'teacher'
    SOURCE_CHOICES = [
        (SOURCE_STUDENT, 'Учащийся'),
        (SOURCE_PARENT, 'Родитель'),
        (SOURCE_TEACHER, 'Педагог'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, db_column='student_id', related_name='requests')
    psychologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='psychologist_id', related_name='handled_requests')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.ForeignKey(RequestStatus, on_delete=models.PROTECT, db_column='status_id', related_name='requests')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'requests'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Обращение {self.student} ({self.status_display})'

    @property
    def status_display(self):
        return {'new': 'Новое', 'in_progress': 'В работе', 'completed': 'Завершено', 'cancelled': 'Отменено'}.get(self.status.name, self.status.name)


class ConsultationForm(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'consultation_forms'
        managed = False

    def __str__(self):
        return {'individual': 'Индивидуальная', 'group': 'Групповая'}.get(self.name, self.name)


class ConsultationStudent(models.Model):
    """Связь консультации с учащимися (многие ко многим)."""
    consultation = models.ForeignKey('Consultation', on_delete=models.CASCADE, db_column='consultation_id', related_name='consultation_students')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, db_column='student_id', related_name='consultation_participations')
    participation_confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Участие подтверждено')
    participation_cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name='Участие отменено (окончательно)')

    class Meta:
        db_table = 'consultation_students'
        managed = False
        unique_together = [['consultation', 'student']]


class Consultation(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True, db_column='request_id', related_name='consultations')
    form = models.ForeignKey(ConsultationForm, on_delete=models.PROTECT, db_column='form_id', related_name='consultations')
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True, verbose_name='Время начала')
    end_time = models.TimeField(blank=True, null=True, verbose_name='Время окончания')
    duration = models.IntegerField()
    result = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Завершена')
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name='Отменена')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    students = models.ManyToManyField(
        'students.Student',
        through='ConsultationStudent',
        related_name='consultations',
        blank=True,
        verbose_name='Учащиеся'
    )

    class Meta:
        db_table = 'consultations'
        managed = False
        ordering = ['-date']

    def __str__(self):
        names = ', '.join(s.full_name for s in self.students.all()[:3])
        if self.students.count() > 3:
            names += '…'
        return f'{names or "—"} — {self.date}'

    @property
    def form_display(self):
        return {'individual': 'Индивидуальная', 'group': 'Групповая'}.get(self.form.name, self.form.name) if self.form_id else '—'

    def students_display(self):
        """Список учащихся для отображения (с учётом старых записей через request)."""
        qs = self.students.all()
        if qs.exists():
            return ', '.join(s.full_name for s in qs.order_by('last_name', 'first_name'))
        if self.request_id:
            return self.request.student.full_name
        return '—'

    def time_display(self):
        """Время начала и конца для отображения."""
        if self.start_time and self.end_time:
            return f'{self.start_time.strftime("%H:%M")} — {self.end_time.strftime("%H:%M")}'
        return None


class Attachment(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, db_column='consultation_id', related_name='attachments')
    file_path = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'attachments'
        managed = False

    @property
    def filename(self):
        """Имя файла для отображения (без пути)."""
        if not self.file_path:
            return '—'
        return self.file_path.replace('\\', '/').split('/')[-1]


class Note(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, db_column='consultation_id', related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='user_id')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'notes'
        managed = False


class Event(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='created_by')

    class Meta:
        db_table = 'events'
        managed = False


class Report(models.Model):
    report_name = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='created_by')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    report_data = models.JSONField(blank=True, null=True, db_column='report_data')

    class Meta:
        db_table = 'reports'
        managed = False


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='user_id')
    action = models.CharField(max_length=100, blank=True, null=True)
    action_date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'logs'
        managed = False


class StudentNotification(models.Model):
    """Уведомление учащегося: назначение консультации или смена статуса обращения."""
    KIND_CONSULTATION_ASSIGNED = 'consultation_assigned'
    KIND_REQUEST_STATUS = 'request_status'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, db_column='student_id', related_name='notifications')
    kind = models.CharField(max_length=30)
    consultation = models.ForeignKey('Consultation', on_delete=models.SET_NULL, null=True, blank=True, db_column='consultation_id', related_name='+')
    request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True, blank=True, db_column='request_id', related_name='+')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'student_notifications'
        managed = False
        ordering = ['-created_at']


class RequestNote(models.Model):
    """Заметка учащегося к обращению."""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, db_column='request_id', related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='user_id')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'request_notes'
        managed = False
        ordering = ['created_at']


class StudentPsychologistChat(models.Model):
    """Личный чат учащегося с закреплённым психологом."""
    student = models.OneToOneField('students.Student', on_delete=models.CASCADE, db_column='student_id', related_name='psychologist_chat')
    psychologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='psychologist_id', related_name='student_chats')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'student_psychologist_chats'
        managed = False
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return f'Чат: {self.student} ↔ {self.psychologist}'


class ChatMessage(models.Model):
    """Сообщение в личном чате учащегося и психолога."""
    chat = models.ForeignKey(StudentPsychologistChat, on_delete=models.CASCADE, db_column='chat_id', related_name='messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='author_id')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_messages'
        managed = False
        ordering = ['created_at']


class ChatMessageRead(models.Model):
    """Отметка прочтения сообщения конкретным пользователем."""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, db_column='message_id', related_name='read_marks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id', related_name='chat_message_reads')
    read_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'chat_message_reads'
        managed = False
        unique_together = [['message', 'user']]
