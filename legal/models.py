# Generated on 2025-05-31 02:59 AM +05
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class LegalDocument(models.Model):
    """Model for versioning legal documents"""
    DOCUMENT_TYPES = (
        ('terms_of_use', 'Terms of Use'),
        ('privacy_policy', 'Privacy Policy'),
        ('public_offer', 'Public Offer'),
        ('booking_rules', 'Booking Rules'),
        ('personal_data_consent', 'Personal Data Consent'),
        ('payment_rules', 'Payment Rules'),
    )
    
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    version = models.CharField(max_length=10)
    content = models.TextField()
    effective_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    language = models.CharField(max_length=2, default='en')
    
    class Meta:
        unique_together = ['document_type', 'version', 'language']
        
    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate previous versions
            LegalDocument.objects.filter(
                document_type=self.document_type,
                language=self.language,
                is_active=True
            ).update(is_active=False)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.get_document_type_display()} v{self.version} ({self.language})"


class DocumentView(models.Model):
    """Model for tracking document views"""
    document_type = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    user_agent = models.TextField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.user or 'Anonymous'} - {self.viewed_at}"
    
    class Meta:
        ordering = ['-viewed_at']
