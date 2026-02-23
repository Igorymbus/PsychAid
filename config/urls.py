"""
URL configuration for подсистема школьного психолога.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('users:login')),
    path('users/', include('users.urls', namespace='users')),
    path('students/', include('students.urls', namespace='students')),
    path('consultations/', include('consultations.urls', namespace='consultations')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)