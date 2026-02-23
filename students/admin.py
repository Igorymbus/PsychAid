from django.contrib import admin
from .models import Student, Classroom, Teacher, Parent


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'subject', 'email')


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'classroom', 'birth_date')
    list_filter = ('classroom',)
    search_fields = ('last_name', 'first_name', 'classroom__name')


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('student', 'last_name', 'first_name', 'phone')
