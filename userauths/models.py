from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.db.models.signals import post_save
from django.utils.html import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from django.dispatch import receiver


from PIL import Image
from shortuuid.django_fields import ShortUUIDField
import os 




GENDER = (
    ("female", "Женский"),
    ("male", "Мужской"),
)

TITLE = (
    ("Mr", "Г-н"),
    ("Mrs", "Г-жа"),
    ("Miss", "Г-жа"),
)


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.user.id, ext)
    return 'user_{0}/{1}'.format(instance.user.id,  filename)

class User(AbstractUser):
    full_name = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Полное имя')
    username = models.CharField(max_length=100, null=True, verbose_name='Имя пользователя')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    phone = models.CharField(max_length=100, null=True, blank=True, verbose_name='Телефон')
    gender = models.CharField(max_length=100, choices=GENDER, null=True, blank=True, verbose_name='Пол')

    otp = models.CharField(max_length=100, null=True, blank=True, verbose_name='OTP код')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username if self.username else str(self.email)
    
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)



class Profile(models.Model):
    pid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123", verbose_name='ID профиля')
    image = models.ImageField(upload_to=user_directory_path, default="default.jpg", null=True, blank=True, verbose_name='Фотография')
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    full_name = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Полное имя')
    phone = models.CharField(max_length=100, null=True, blank=True, verbose_name='Телефон')
    gender = models.CharField(max_length=100, choices=GENDER, null=True, blank=True, verbose_name='Пол')

    country = models.CharField(max_length=100, null=True, blank=True, verbose_name='Страна')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='Город')
    address = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Адрес')
    
    wallet = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, verbose_name='Кошелек')
    verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Дата создания')

    class Meta:
        ordering = ["-date"]
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        if self.full_name:
            return f"{self.full_name}"
        else:
            return f"{self.user.username}"
        
    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.username
            
        super(Profile, self).save(*args, **kwargs) 
    
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" />' % (self.image))

    thumbnail.short_description = 'Миниатюра'
    
    
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


@receiver(models.signals.pre_delete, sender=Profile)
def delete_image_file(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path
        if os.path.exists(image_path):
            os.remove(image_path)


class UserConsent(models.Model):
    """Model for tracking user consents - Added on 2025-05-31 02:59 AM +05"""
    CONSENT_TYPES = (
        ('terms_of_use', 'Условия использования'),
        ('privacy_policy', 'Политика конфиденциальности'),
        ('personal_data', 'Обработка персональных данных'),
        ('marketing', 'Маркетинговые коммуникации'),
        ('booking_terms', 'Условия бронирования'),
        ('payment_terms', 'Условия оплаты'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    consent_type = models.CharField(max_length=50, choices=CONSENT_TYPES, verbose_name='Тип согласия')
    given_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата предоставления')
    user_agent = models.TextField(verbose_name='User Agent')
    document_version = models.CharField(max_length=10, default='1.0', verbose_name='Версия документа')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    withdrawn_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отзыва')
    
    class Meta:
        unique_together = ['user', 'consent_type', 'document_version']
        ordering = ['-given_at']
        verbose_name = 'Согласие пользователя'
        verbose_name_plural = 'Согласия пользователей'
        
    def __str__(self):
        return f"{self.user} - {self.consent_type} - {self.document_version}"

