from django import forms
from django.core.exceptions import ValidationError
from .models import RoomType
import json
from datetime import datetime

class RoomTypeAdminForm(forms.ModelForm):
    dynamic_pricing_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        help_text="Введите цены по датам в формате JSON: {'YYYY-MM-DD': price}. Например: {'2025-05-15': 150.00}"
    )

    class Meta:
        model = RoomType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если есть данные в dynamic_pricing, преобразуем их в JSON-строку для отображения
        if self.instance and self.instance.dynamic_pricing:
            self.fields['dynamic_pricing_input'].initial = json.dumps(
                self.instance.dynamic_pricing, indent=2, cls=DjangoJSONEncoder
            )

    def clean_dynamic_pricing_input(self):
        data = self.cleaned_data.get('dynamic_pricing_input')
        if data:
            try:
                # Проверяем, что введенные данные — валидный JSON
                pricing = json.loads(data)
                if not isinstance(pricing, dict):
                    raise ValidationError("Динамические цены должны быть словарем.")
                
                # Проверяем формат дат и значений
                for date_str, price in pricing.items():
                    try:
                        datetime.strptime(date_str, "%Y-%m-%d")
                        if not isinstance(price, (int, float)) or price < 0:
                            raise ValidationError(f"Цена для {date_str} должна быть положительным числом.")
                    except ValueError:
                        raise ValidationError(f"Неверный формат даты: {date_str}. Используйте YYYY-MM-DD.")
                return pricing
            except json.JSONDecodeError:
                raise ValidationError("Неверный формат JSON.")
        return {}

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.dynamic_pricing = self.cleaned_data['dynamic_pricing_input']
        if commit:
            instance.save()
        return instance