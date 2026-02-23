"""
Модели: teachers, classrooms, students, parents.
managed=False — таблицы создаются schema.sql.
"""
from django.db import models


class Teacher(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'teachers'
        managed = False

    def __str__(self):
        return f'{self.last_name or ""} {self.first_name or ""}'.strip() or '-'


class Classroom(models.Model):
    name = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, db_column='teacher_id', related_name='classrooms')

    class Meta:
        db_table = 'classrooms'
        managed = False

    def __str__(self):
        return self.name


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, db_column='class_id', related_name='students')
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'students'
        managed = False
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'.strip()

    @property
    def class_name(self):
        return self.classroom.name if self.classroom_id else '—'


class Parent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id', related_name='parents')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'parents'
        managed = False
