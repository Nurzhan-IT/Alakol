from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class CaseInsensitiveEmailBackend(ModelBackend):
    """
    Бэкенд аутентификации, который позволяет входить в систему, используя email
    без учета регистра.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            # Преобразуем email в нижний регистр для поиска
            username = username.lower()
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Если пользователь не найден, возвращаем None
            return None
        else:
            # Проверяем пароль
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None 