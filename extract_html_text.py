#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Text Extractor
Скрипт для извлечения текста из HTML файлов и сохранения в TXT формате.
Специально разработан для обработки юридических документов с точным извлечением текста.

Автор: AI Assistant
Дата создания: 2025
"""

import os
import glob
import logging
from pathlib import Path
from bs4 import BeautifulSoup, Comment
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def clean_text(text):
    """
    Очистка и форматирование извлеченного текста.
    Удаляет лишние пробелы, переносы строк и форматирует текст для читаемости.
    
    Args:
        text (str): Исходный текст
        
    Returns:
        str: Очищенный и отформатированный текст
    """
    if not text:
        return ""
    
    # Удаляем множественные пробелы и табуляции
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Удаляем множественные переносы строк (оставляем максимум 2)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Удаляем пробелы в начале и конце строк
    lines = [line.strip() for line in text.split('\n')]
    
    # Удаляем пустые строки в начале и конце
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    
    return '\n'.join(lines)


def extract_text_from_html(html_file_path):
    """
    Извлекает текст из HTML файла с использованием BeautifulSoup.
    Удаляет script, style теги и HTML комментарии.
    
    Args:
        html_file_path (str): Путь к HTML файлу
        
    Returns:
        str: Извлеченный текст или пустая строка в случае ошибки
    """
    try:
        # Чтение HTML файла с UTF-8 кодировкой
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Парсинг HTML с помощью BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Удаление script и style тегов
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        
        # Удаление HTML комментариев
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Удаление Django template тегов и переменных
        for template_tag in soup.find_all(string=re.compile(r'{%.*?%}|{{.*?}}')):
            template_tag.extract()
        
        # Извлечение текста
        text = soup.get_text()
        
        # Очистка и форматирование текста
        cleaned_text = clean_text(text)
        
        logger.info(f"Успешно извлечен текст из {html_file_path}")
        return cleaned_text
        
    except FileNotFoundError:
        logger.error(f"Файл не найден: {html_file_path}")
        return ""
    except UnicodeDecodeError:
        logger.error(f"Ошибка декодирования файла: {html_file_path}")
        try:
            # Попытка чтения с другой кодировкой
            with open(html_file_path, 'r', encoding='windows-1251') as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            for template_tag in soup.find_all(string=re.compile(r'{%.*?%}|{{.*?}}')):
                template_tag.extract()
            text = soup.get_text()
            cleaned_text = clean_text(text)
            logger.info(f"Успешно извлечен текст из {html_file_path} с кодировкой windows-1251")
            return cleaned_text
        except Exception as e:
            logger.error(f"Ошибка при чтении файла с альтернативной кодировкой {html_file_path}: {e}")
            return ""
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {html_file_path}: {e}")
        return ""


def save_text_to_file(text, output_file_path):
    """
    Сохраняет текст в TXT файл с UTF-8 кодировкой.
    
    Args:
        text (str): Текст для сохранения
        output_file_path (str): Путь к выходному файлу
        
    Returns:
        bool: True если успешно сохранено, False в противном случае
    """
    try:
        # Создание директории если она не существует
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        # Сохранение текста в файл
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        
        logger.info(f"Текст сохранен в {output_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла {output_file_path}: {e}")
        return False


def process_html_files(input_directory, output_directory):
    """
    Обрабатывает все HTML файлы в указанной директории.
    Извлекает текст и сохраняет в соответствующие TXT файлы.
    
    Args:
        input_directory (str): Путь к директории с HTML файлами
        output_directory (str): Путь к директории для сохранения TXT файлов
        
    Returns:
        tuple: (количество успешно обработанных файлов, общее количество файлов)
    """
    if not os.path.exists(input_directory):
        logger.error(f"Входная директория не существует: {input_directory}")
        return 0, 0
    
    # Поиск всех HTML файлов в директории
    html_pattern = os.path.join(input_directory, "*.html")
    html_files = glob.glob(html_pattern)
    
    if not html_files:
        logger.warning(f"HTML файлы не найдены в директории: {input_directory}")
        return 0, 0
    
    logger.info(f"Найдено {len(html_files)} HTML файлов для обработки")
    
    processed_count = 0
    total_count = len(html_files)
    
    # Создание выходной директории если она не существует
    os.makedirs(output_directory, exist_ok=True)
    
    # Обработка каждого HTML файла
    for html_file in html_files:
        try:
            # Получение имени файла без расширения
            file_name = Path(html_file).stem
            
            # Создание пути для выходного TXT файла
            txt_file_path = os.path.join(output_directory, f"{file_name}.txt")
            
            logger.info(f"Обработка файла: {html_file}")
            
            # Извлечение текста из HTML
            extracted_text = extract_text_from_html(html_file)
            
            # Сохранение текста в TXT файл
            if save_text_to_file(extracted_text, txt_file_path):
                processed_count += 1
                logger.info(f"Файл успешно обработан: {file_name}.html -> {file_name}.txt")
            else:
                logger.error(f"Ошибка при сохранении файла: {file_name}.txt")
                
        except Exception as e:
            logger.error(f"Неожиданная ошибка при обработке файла {html_file}: {e}")
    
    return processed_count, total_count


def main():
    """
    Основная функция программы.
    Обрабатывает HTML файлы из папки legal и сохраняет TXT файлы в created_by_ai.
    """
    # Определение путей
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "templates", "legal_en")
    output_dir = os.path.join(script_dir, "documents", "exported_from_html", "en")
    
    logger.info("=" * 60)
    logger.info("ЗАПУСК HTML TEXT EXTRACTOR")
    logger.info("=" * 60)
    logger.info(f"Входная директория: {input_dir}")
    logger.info(f"Выходная директория: {output_dir}")
    
    # Проверка существования входной директории
    if not os.path.exists(input_dir):
        logger.error(f"Входная директория не найдена: {input_dir}")
        logger.info("Убедитесь, что скрипт находится в корневой папке проекта")
        return
    
    # Обработка HTML файлов
    processed, total = process_html_files(input_dir, output_dir)
    
    # Вывод результатов
    logger.info("=" * 60)
    logger.info("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    logger.info("=" * 60)
    logger.info(f"Всего файлов найдено: {total}")
    logger.info(f"Успешно обработано: {processed}")
    logger.info(f"Не удалось обработать: {total - processed}")
    
    if processed > 0:
        logger.info(f"TXT файлы сохранены в: {output_dir}")
        logger.info("Обработка завершена успешно!")
    else:
        logger.warning("Ни один файл не был успешно обработан")


if __name__ == "__main__":
    main() 