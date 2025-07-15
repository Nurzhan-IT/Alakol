from django import forms
from django.core.exceptions import ValidationError
from .models import RoomUnavailability


class RoomUnavailabilityForm(forms.ModelForm):
    class Meta:
        model = RoomUnavailability
        fields = ['room', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError({
                    'end_date': 'Дата окончания не может быть раньше даты начала'
                })

        return cleaned_data