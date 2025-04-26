from django import forms
from django.utils.safestring import mark_safe
import os

class IconSelectWidget(forms.Select):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)

    def render(self, name, value, attrs=None, renderer=None):
        # Рендеринг основного select с иконками
        output = super().render(name, value, attrs, renderer)

        # Получаем путь к иконке, если значение выбрано
        icon_url = os.path.join('/static/icons/', value) if value else ''
        
        # HTML для показа превью иконки
        icon_preview = f'<img id="icon-preview-{name}" src="{icon_url}" style="width: 40px; height: 40px;">' if value else '<img id="icon-preview-{name}" style="width: 40px; height: 40px;">'
        
        # Добавляем JavaScript для моментального обновления иконки при выборе
        js_script = f'''
            <script type="text/javascript">
                document.addEventListener('DOMContentLoaded', function() {{
                    var selectElement = document.getElementById('id_{name}');
                    var iconPreview = document.getElementById('icon-preview-{name}');
                    
                    // Функция для обновления превью иконки
                    function updateIconPreview() {{
                        var selectedIcon = selectElement.value;
                        if (selectedIcon) {{
                            iconPreview.src = '/static/icons/' + selectedIcon;
                        }} else {{
                            iconPreview.src = '';
                        }}
                    }}

                    // Инициализируем превью при загрузке страницы
                    updateIconPreview();

                    // Добавляем слушатель на изменение селектора
                    selectElement.addEventListener('change', function() {{
                        updateIconPreview();
                    }});
                }});
            </script>
        '''
        
        return mark_safe(output + icon_preview + js_script)
