"""
Модели: roles, users. managed=False - таблицы создаются schema.sql.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'roles'
        managed = False

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **kwargs):
        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **kwargs):
        admin_role = Role.objects.filter(name='admin').first()
        if admin_role:
            kwargs.setdefault('role', admin_role)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(username, password, **kwargs)


class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255, db_column='password_hash')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, db_column='role_id', related_name='users')
    student = models.ForeignKey('students.Student', on_delete=models.SET_NULL, null=True, blank=True, db_column='student_id', related_name='user_accounts')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_administrator(self):
        return self.role.name == 'admin'

    @property
    def role_name(self):
        return self.role.name if self.role_id else None

    def get_role_display(self):
        return {'admin': 'Администратор', 'psychologist': 'Школьный психолог', 'student': 'Учащийся'}.get(self.role_name, self.role_name or '—')


class UserSecurityPhrase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id', related_name='security_phrase')
    phrase_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'user_security_phrases'
        managed = False
