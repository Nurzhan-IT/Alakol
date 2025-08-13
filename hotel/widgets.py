from django import forms
from django.utils.safestring import mark_safe
import os

class DDMMDateInput(forms.TextInput):
    """
    Text input for DD.MM date without year with client-side mask and auto dot.
    """
    input_type = 'text'

    def __init__(self, attrs=None):
        base_attrs = {
            'placeholder': 'ДД.ММ',
            'maxlength': '5',
            'pattern': r'\d{2}\.\d{2}',
            'inputmode': 'numeric',
            'style': 'width:120px',
        }
        if attrs:
            base_attrs.update(attrs)
        super().__init__(base_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)
        field_id = (attrs or {}).get('id', f'id_{name}')
        js = f'''
        <script>(function(){{
          var el=document.getElementById('{field_id}');
          if(!el) return;
          function format(v){{
            v = (v||'').replace(/[^0-9]/g,'');
            if (v.length > 4) v = v.slice(0,4);
            if (v.length >= 3) return v.slice(0,2)+'.'+v.slice(2);
            if (v.length >= 1) return v;
            return '';
          }}
          el.addEventListener('input', function(e){{
            var cur = e.target.value;
            var formatted = format(cur);
            if (cur !== formatted) {{
              var pos = e.target.selectionStart;
              e.target.value = formatted;
              // try to keep caret near end
              e.target.selectionStart = e.target.selectionEnd = formatted.length;
            }}
          }});
          el.addEventListener('blur', function(e){{
            var v = e.target.value;
            if (!v) return;
            var m = /^\d{2}\.\d{2}$/.test(v);
            if(!m) {{ e.target.classList.add('error'); return; }}
            var d=parseInt(v.slice(0,2),10), mth=parseInt(v.slice(3),10);
            var daysIn=[31,29,31,30,31,30,31,31,30,31,30,31];
            var ok = mth>=1 && mth<=12 && d>=1 && d<=daysIn[mth-1];
            if(!ok) e.target.classList.add('error'); else e.target.classList.remove('error');
          }});
        }})();</script>
        '''
        return mark_safe(input_html + js)

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


class AgeRangeSliderWidget(forms.TextInput):
    """
    Кастомный виджет двухползункового слайдера для выбора диапазона возраста.
    Рендерится как скрытое числовое поле age_min + визуальный слайдер.
    Значение age_max читается/записывается через соответствующий скрытый input,
    который должен быть отрендерен отдельным полем формы (HiddenInput) рядом.
    """

    input_type = 'number'

    def __init__(self, attrs=None, min_age=0, max_age=99, step=1):
        base_attrs = {
            'min': str(min_age),
            'max': str(max_age),
            'step': str(step),
            'style': 'display:none',
        }
        if attrs:
            base_attrs.update(attrs)
        self._min_age = min_age
        self._max_age = max_age
        self._step = step
        super().__init__(base_attrs)

    class Media:
        css = {
            'all': (
                'admin/css/age_range_slider.css',
            )
        }
        js = (
            'admin/js/age_range_slider.js',
        )

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)

        field_id = (attrs or {}).get('id', f'id_{name}')
        slider_id = f'{field_id}__slider'

        # Не указываем data-*-input-id атрибуты, JS найдет поля сам
        slider_html = f'''
        <div class="age-range-slider" id="{slider_id}"
             data-min="{self._min_age}" data-max="{self._max_age}" data-step="{self._step}">
            <div class="ars-track"></div>
            <div class="ars-range"></div>
            <div class="ars-handle ars-handle-min"><div class="ars-label ars-label-min">{value if value is not None else self._min_age}</div></div>
            <div class="ars-handle ars-handle-max"><div class="ars-label ars-label-max"></div></div>
        </div>
        '''

        return mark_safe(input_html + slider_html)