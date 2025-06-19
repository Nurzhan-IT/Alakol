#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def main():
    """Заполняет пустые переводы в django.po файле"""
    
    po_file = "locale/ru/LC_MESSAGES/django.po"
    
    # Основные переводы из русских .txt файлов
    translations = {
        "HOTEL BOOKING AND CANCELLATION RULES": "ПРАВИЛА БРОНИРОВАНИЯ И ОТМЕНЫ БРОНИРОВАНИЯ",
        "eKol HOTEL BOOKING SYSTEM": "СИСТЕМЫ БРОНИРОВАНИЯ ОТЕЛЕЙ eKol",
        "June 19, 2025": "19 Июня, 2025",
        "Effective Date:": "Дата вступления в силу:",
        "Document Version:": "Версия документа:",
        "1. GENERAL PROVISIONS": "1. ОБЩИЕ ПОЛОЖЕНИЯ",
        "2. BOOKING CONDITIONS": "2. УСЛОВИЯ БРОНИРОВАНИЯ",
        "These Rules determine the terms and conditions for booking hotel rooms, as well as the conditions for changing and canceling bookings through the website [WEBSITE ADDRESS].": "Настоящие Правила определяют условия и порядок бронирования номеров в отелях, а также условия изменения и отмены бронирования через веб-сайт [АДРЕС САЙТА].",
        "The Rules apply to all users of the booking system and are an integral part of the Public Offer for hotel booking services.": "Правила действуют для всех пользователей системы бронирования и являются неотъемлемой частью Публичной оферты на оказание услуг бронирования отелей.",
        "By accepting the booking terms, the User agrees to these Rules in full.": "Принимая условия бронирования, Пользователь соглашается с настоящими Правилами в полном объеме.",
    }
    
    # Читаем файл
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filled_count = 0
    
    # Заполняем переводы
    for english, russian in translations.items():
        pattern = r'(msgid "' + re.escape(english) + r'"\s*\n)msgstr ""'
        replacement = r'\1msgstr "' + russian.replace('"', '\\"') + '"'
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if new_content != content:
            filled_count += 1
            content = new_content
            print(f"Заполнен: {english[:50]}...")
    
    # Сохраняем файл
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nЗаполнено переводов: {filled_count}")

if __name__ == "__main__":
    main() 