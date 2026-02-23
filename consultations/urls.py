from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    # Обращения
    path('requests/', views.RequestListView.as_view(), name='request_list'),
    path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:pk>/edit/', views.RequestUpdateView.as_view(), name='request_edit'),
    path('requests/<int:pk>/complete/', views.RequestCompleteView.as_view(), name='request_complete'),
    path('requests/<int:pk>/cancel/', views.RequestCancelView.as_view(), name='request_cancel'),
    path('requests/<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request_delete'),
    # Консультации (журнал)
    path('journal/', views.ConsultationListView.as_view(), name='consultation_list'),
    path('journal/create/', views.ConsultationCreateView.as_view(), name='consultation_create'),
    path('journal/<int:pk>/', views.ConsultationDetailView.as_view(), name='consultation_detail'),
    path('journal/<int:pk>/notes/add/', views.ConsultationNoteCreateView.as_view(), name='consultation_note_add'),
    path('journal/<int:pk>/attachments/', views.ConsultationAttachmentUploadView.as_view(), name='consultation_attachment_upload'),
    path('journal/<int:pk>/attachments/<int:attachment_id>/delete/', views.ConsultationAttachmentDeleteView.as_view(), name='consultation_attachment_delete'),
    path('journal/<int:pk>/assign-psychologist/', views.ConsultationAssignPsychologistView.as_view(), name='consultation_assign_psychologist'),
    path('journal/<int:pk>/edit/', views.ConsultationUpdateView.as_view(), name='consultation_edit'),
    path('journal/<int:pk>/complete/', views.ConsultationCompleteView.as_view(), name='consultation_complete'),
    path('journal/<int:pk>/cancel/', views.ConsultationCancelView.as_view(), name='consultation_cancel'),
    path('journal/<int:pk>/delete/', views.ConsultationDeleteView.as_view(), name='consultation_delete'),
    path('admin/database/', views.DatabaseMaintenanceView.as_view(), name='database_maintenance'),
    path('admin/database/download/<str:filename>/', views.DatabaseBackupDownloadView.as_view(), name='database_backup_download'),
    path('admin/database/delete/<str:filename>/', views.DatabaseBackupDeleteView.as_view(), name='database_backup_delete'),
    # Отчёты
    path('reports/', views.ReportView.as_view(), name='report'),
    path('reports/student/<int:pk>/dynamics/', views.StudentDynamicsView.as_view(), name='student_dynamics'),
    # Экспорт (психолог — три отчёта; админ — по консультациям)
    path('reports/export/students-report/pdf/', views.ExportStudentsReportPDFView.as_view(), name='export_students_report_pdf'),
    path('reports/export/students-report/excel/', views.ExportStudentsReportExcelView.as_view(), name='export_students_report_excel'),
    path('reports/export/dynamics/pdf/', views.ExportDynamicsPDFView.as_view(), name='export_dynamics_pdf'),
    path('reports/export/dynamics/excel/', views.ExportDynamicsExcelView.as_view(), name='export_dynamics_excel'),
    path('reports/export/workload/pdf/', views.ExportWorkloadPDFView.as_view(), name='export_workload_pdf'),
    path('reports/export/students/pdf/', views.ExportStudentsPDFView.as_view(), name='export_students_pdf'),
    path('reports/export/students/excel/', views.ExportStudentsExcelView.as_view(), name='export_students_excel'),
    path('reports/export/consultations/pdf/', views.ExportConsultationsPDFView.as_view(), name='export_consultations_pdf'),
    path('reports/export/consultations/excel/', views.ExportConsultationsExcelView.as_view(), name='export_consultations_excel'),
    # Личный кабинет учащегося
    path('my/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('my/requests/', views.MyRequestListView.as_view(), name='my_request_list'),
    path('my/requests/create/', views.MyRequestCreateView.as_view(), name='my_request_create'),
    path('my/requests/<int:pk>/cancel/', views.MyRequestCancelView.as_view(), name='my_request_cancel'),
    path('my/requests/<int:pk>/', views.MyRequestDetailView.as_view(), name='my_request_detail'),
    path('my/consultations/', views.MyConsultationListView.as_view(), name='my_consultation_list'),
    path('my/consultations/<int:pk>/confirm/', views.MyConsultationConfirmParticipationView.as_view(), name='my_consultation_confirm'),
    path('my/consultations/<int:pk>/cancel-participation/', views.MyConsultationCancelParticipationView.as_view(), name='my_consultation_cancel_participation'),
    # Чаты обратной связи (учащийся ↔ психолог)
    path('my/chat/', views.StudentChatView.as_view(), name='student_chat'),
    path('chats/', views.PsychologistChatListView.as_view(), name='psychologist_chat_list'),
    path('chats/<int:pk>/', views.PsychologistChatDetailView.as_view(), name='psychologist_chat_detail'),
]
