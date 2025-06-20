#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

def fix_legal_translations(po_file_path):
    """
    Заполняет пустые msgstr для legal файлов значениями из msgid
    """
    
    # Список путей к файлам legal, для которых нужно заполнить переводы
    legal_files = [
        'templates\\legal\\hotel_owner_docs\\hotel_owner_agreement.html',
        'templates\\legal\\booking_rules.html',
        'templates\\legal\\payment_rules.html',
        'templates\\legal\\personal_data_consent.html',
        'templates\\legal\\privacy_policy.html',
        'templates\\legal\\public_offer.html',
        'templates\\legal\\terms_of_use.html'
    ]
    
    try:
        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разбиваем содержимое на строки
        lines = content.split('\n')
        
        # Переменные для отслеживания состояния
        i = 0
        modified = False
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Ищем строки с комментариями, указывающими на файлы
            if line.startswith('#:') and any(legal_file in line for legal_file in legal_files):
                # Нашли комментарий для legal файла
                # Теперь ищем соответствующий msgid и msgstr
                j = i + 1
                msgid_found = False
                msgid_value = ""
                msgstr_line_index = -1
                
                # Пропускаем дополнительные комментарии и контекст
                while j < len(lines):
                    current_line = lines[j].strip()
                    
                    if current_line.startswith('msgid '):
                        # Нашли msgid
                        msgid_found = True
                        msgid_match = re.match(r'msgid\s+"(.*)"', current_line)
                        if msgid_match:
                            msgid_value = msgid_match.group(1)
                        
                        # Проверяем, есть ли многострочный msgid
                        k = j + 1
                        while k < len(lines) and lines[k].strip().startswith('"') and not lines[k].strip().startswith('msgstr'):
                            # Добавляем продолжение многострочного msgid
                            continuation_match = re.match(r'"(.*)"', lines[k].strip())
                            if continuation_match:
                                msgid_value += continuation_match.group(1)
                            k += 1
                        j = k - 1
                        
                    elif current_line.startswith('msgstr ') and msgid_found:
                        # Нашли msgstr
                        msgstr_match = re.match(r'msgstr\s+"(.*)"', current_line)
                        if msgstr_match and msgstr_match.group(1) == "":
                            # msgstr пустой, заполняем его значением из msgid
                            if msgid_value:
                                lines[j] = f'msgstr "{msgid_value}"'
                                modified = True
                                print(f"Заполнен перевод: {msgid_value}")
                        break
                    
                    elif current_line.startswith('#:') or current_line.startswith('msgid '):
                        # Начинается новая запись
                        break
                    
                    j += 1
            
            i += 1
        
        if modified:
            # Сохраняем изменения
            with open(po_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"Файл '{po_file_path}' успешно обновлен!")
        else:
            print("Пустые переводы для legal файлов не найдены или уже заполнены.")
            
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return False
    
    return modified

if __name__ == "__main__":
    po_file = "locale/ru/LC_MESSAGES/django.po"
    fix_legal_translations(po_file) 