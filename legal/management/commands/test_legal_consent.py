from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from legal.utils import check_user_consent, save_user_consent, get_document_version
from userauths.models import UserConsent

User = get_user_model()


class Command(BaseCommand):
    help = 'Тестирует систему согласий для legal agreements'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email пользователя для тестирования',
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Только проверить согласие, не создавать новое',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Тестирование системы legal consent...')
        )

        user_email = options.get('user_email')
        if not user_email:
            # Используем первого superuser'а для теста
            try:
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.filter(is_staff=True).first()
                if not user:
                    self.stdout.write(
                        self.style.ERROR('Не найден пользователь для тестирования')
                    )
                    return
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('Не найден пользователь для тестирования')
                )
                return
        else:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Пользователь с email {user_email} не найден')
                )
                return

        self.stdout.write(f'Тестируем для пользователя: {user.email}')

        # Получаем версию документа
        document_version = get_document_version('hotel_owner_agreement')
        self.stdout.write(f'Версия документа: {document_version}')

        # Проверяем существующее согласие
        has_consent = check_user_consent(user, 'hotel_owner_agreement', document_version)
        self.stdout.write(f'Имеет согласие: {has_consent}')

        if not options.get('check_only'):
            if not has_consent:
                # Создаем согласие
                self.stdout.write('Создаем согласие...')
                consent = save_user_consent(
                    user=user,
                    consent_type='hotel_owner_agreement',
                    document_version=document_version,
                    user_agent='Test Command'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Согласие создано: {consent}')
                )
            else:
                self.stdout.write('Согласие уже существует')

        # Показываем все согласия пользователя
        consents = UserConsent.objects.filter(user=user)
        self.stdout.write(f'\nВсе согласия пользователя ({consents.count()}):')
        for consent in consents:
            self.stdout.write(
                f'- {consent.consent_type} v{consent.document_version} '
                f'(активно: {consent.is_active}, дата: {consent.given_at})'
            )

        self.stdout.write(
            self.style.SUCCESS('\nТестирование завершено!')
        ) 