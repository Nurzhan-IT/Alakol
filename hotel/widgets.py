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

class RoomTypeSelectWidget(forms.Select):
    """
    Виджет для отображения типа номера только по названию для пользователей группы Manager
    """
    
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)
    
    def label_from_instance(self, obj):
        """
        Возвращает только название типа номера вместо полного описания
        """
        return obj.type if hasattr(obj, 'type') else str(obj)

    def render(self, name, value, attrs=None, renderer=None):
        # Получаем стандартный HTML для select
        output = super().render(name, value, attrs, renderer)
        
        # Добавляем JavaScript для замены текста в опциях
        js_script = f'''
            <script type="text/javascript">
                document.addEventListener('DOMContentLoaded', function() {{
                    var selectElement = document.getElementById('id_{name}');
                    if (selectElement) {{
                        // Перебираем все опции и оставляем только название типа
                        var options = selectElement.querySelectorAll('option');
                        options.forEach(function(option) {{
                            if (option.value && option.textContent.includes(' - ')) {{
                                // Извлекаем только первую часть до первого ' - '
                                var parts = option.textContent.split(' - ');
                                option.textContent = parts[0];
                            }}
                        }});
                    }}
                }});
            </script>
        '''
        
        return mark_safe(output + js_script)

class SimpleTextEditorWidget(forms.Textarea):
    """
    Простой текстовый редактор с базовым форматированием (без заголовков)
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'simple-text-editor',
            'rows': 10,
            'cols': 80,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    class Media:
        css = {
            'all': ('css/simple_editor.css',)
        }
        js = ('js/simple_editor.js',)
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Рендерим виджет с кнопками форматирования (без заголовков)
        """
        textarea_html = super().render(name, value, attrs, renderer)
        
        editor_id = attrs.get('id', f'id_{name}')
        
        toolbar_html = f'''
        <div class="simple-editor-toolbar" data-editor="{editor_id}">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="bold" title="Жирный">
                <i class="fas fa-bold"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="italic" title="Курсив">
                <i class="fas fa-italic"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="underline" title="Подчеркнутый">
                <i class="fas fa-underline"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="insertUnorderedList" title="Маркированный список">
                <i class="fas fa-list-ul"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="insertOrderedList" title="Нумерованный список">
                <i class="fas fa-list-ol"></i>
            </button>
        </div>
        '''
        
        return mark_safe(f'''
        <div class="simple-editor-container">
            {toolbar_html}
            {textarea_html}
        </div>
        ''')
