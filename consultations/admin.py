from django.contrib import admin
from .models import Request, Consultation, RequestStatus, ConsultationForm


@admin.register(RequestStatus)
class RequestStatusAdmin(admin.ModelAdmin):
    list_display = ('__str__',)  # отображение на русском через __str__


@admin.register(ConsultationForm)
class ConsultationFormAdmin(admin.ModelAdmin):
    list_display = ('__str__',)  # отображение на русском через __str__


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'source', 'status', 'psychologist', 'created_at')
    list_filter = ('status', 'source')
    search_fields = ('student__last_name', 'student__first_name')


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('request', 'date', 'form', 'duration', 'result')
    list_filter = ('date', 'form')
    search_fields = ('request__student__last_name', 'result')
