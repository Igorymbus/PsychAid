"""Сигналы и хелперы для уведомлений учащегося."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ConsultationStudent, StudentNotification


def notify_request_status_changed(request_obj):
    """Создать уведомление учащемуся об изменении статуса обращения."""
    if not request_obj or not request_obj.student_id:
        return
    StudentNotification.objects.create(
        student_id=request_obj.student_id,
        kind=StudentNotification.KIND_REQUEST_STATUS,
        request_id=request_obj.pk,
    )


@receiver(post_save, sender=ConsultationStudent)
def on_consultation_student_created(sender, instance, created, **kwargs):
    """При назначении учащегося на консультацию — уведомление."""
    if created:
        StudentNotification.objects.create(
            student_id=instance.student_id,
            kind=StudentNotification.KIND_CONSULTATION_ASSIGNED,
            consultation_id=instance.consultation_id,
        )
