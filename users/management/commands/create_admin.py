"""
Создать учётную запись администратора (суперпользователя).
Использование: python manage.py create_admin
             python manage.py create_admin --username admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт суперпользователя (администратора) для входа в систему и в /admin/'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Логин (по умолчанию: admin)')

    def handle(self, *args, **options):
        username = options['username']
        if User.objects.filter(username=username).exists():
            u = User.objects.get(username=username)
            admin_role = Role.objects.filter(name='admin').first()
            if admin_role:
                u.role = admin_role
            u.is_staff = True
            u.is_superuser = True
            u.is_active = True
            u.save()
            self.stdout.write(self.style.SUCCESS(f'Пользователь {username} обновлён: is_staff, is_superuser, роль «Администратор».'))
            self.stdout.write('Задайте новый пароль: python manage.py changepassword ' + username)
            return

        import getpass
        p1 = getpass.getpass('Пароль: ')
        p2 = getpass.getpass('Пароль (ещё раз): ')
        if p1 != p2 or not p1:
            self.stderr.write(self.style.ERROR('Пароли не совпали или пустой. Выход.'))
            return
        User.objects.create_superuser(username=username, password=p1)
        self.stdout.write(self.style.SUCCESS(f'Администратор {username} создан. Вход: /users/login/ или /admin/'))
