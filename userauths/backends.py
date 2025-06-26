from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class CaseInsensitiveEmailBackend(ModelBackend):
    """
    Бэкенд аутентификации, который позволяет входить в систему, используя email
    без учета регистра для Django Admin и обычной аутентификации.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Получаем username из разных источников (для совместимости с Django Admin)
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        try:
            # Преобразуем email в нижний регистр для поиска
            username_lower = username.lower()
            
            # Ищем пользователей по email без учета регистра
            user = User.objects.get(Q(email__iexact=username_lower))
            
        except User.DoesNotExist:
            # Если пользователь не найден, возвращаем None
            return None
        except User.MultipleObjectsReturned:
            # Если найдено несколько пользователей (не должно быть при unique=True)
            return None
        else:
            # Проверяем пароль
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None 