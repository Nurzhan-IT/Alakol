#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой HTML Text Extractor
Упрощенная версия скрипта для извлечения текста из HTML файлов
"""

import os
import glob
from bs4 import BeautifulSoup
import re

def extract_text_from_html_simple(html_file):
    """Простое извлечение текста из HTML файла"""
    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
        
        # Удаляем скрипты, стили и комментарии
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        # Удаляем Django теги
        for template_tag in soup.find_all(string=re.compile(r'{%.*?%}|{{.*?}}')):
            template_tag.extract()
        
        # Получаем текст
        text = soup.get_text()
        
        # Очищаем текст
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    except:
        return ""

def main():
    """Основная функция"""
    input_dir = "templates/legal"
    output_dir = "documents/created_by_ai"
    
    if not os.path.exists(input_dir):
        print(f"Папка {input_dir} не найдена!")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    html_files = glob.glob(os.path.join(input_dir, "*.html"))
    
    for html_file in html_files:
        file_name = os.path.splitext(os.path.basename(html_file))[0]
        txt_file = os.path.join(output_dir, f"{file_name}.txt")
        
        text = extract_text_from_html_simple(html_file)
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✓ {file_name}.html -> {file_name}.txt")
    
    print(f"\nВсе файлы сохранены в папку: {output_dir}")

if __name__ == "__main__":
    main() 