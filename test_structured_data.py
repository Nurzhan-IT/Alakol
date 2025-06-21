#!/usr/bin/env python3
"""
Скрипт для тестирования структурированных данных сайта
Проверяет наличие и корректность Schema.org разметки
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_json_ld(html_content):
    """Извлекает JSON-LD данные из HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    structured_data = []
    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)
            structured_data.append(data)
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON-LD: {e}")
    
    return structured_data

def validate_hotel_schema(data):
    """Проверяет схему Hotel"""
    required_fields = ['@context', '@type', 'name', 'address']
    errors = []
    
    if data.get('@type') != 'Hotel':
        return errors
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Отсутствует обязательное поле: {field}")
    
    # Проверяем адрес
    if 'address' in data:
        address = data['address']
        if isinstance(address, dict):
            if '@type' not in address or address['@type'] != 'PostalAddress':
                errors.append("Неправильный тип адреса")
            if 'streetAddress' not in address:
                errors.append("Отсутствует улица в адресе")
    
    # Проверяем рейтинг
    if 'aggregateRating' in data:
        rating = data['aggregateRating']
        if 'ratingValue' not in rating or 'reviewCount' not in rating:
            errors.append("Неполные данные рейтинга")
    
    return errors

def test_page_structured_data(url):
    """Тестирует структурированные данные страницы"""
    print(f"\n🔍 Тестирование: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Извлекаем структурированные данные
        structured_data = extract_json_ld(response.text)
        
        if not structured_data:
            print("❌ Структурированные данные не найдены")
            return False
        
        print(f"✅ Найдено {len(structured_data)} блоков структурированных данных")
        
        # Проверяем каждый блок
        for i, data in enumerate(structured_data, 1):
            print(f"\n📋 Блок {i}: {data.get('@type', 'Unknown')}")
            
            if data.get('@type') == 'Hotel':
                errors = validate_hotel_schema(data)
                if errors:
                    print("❌ Ошибки в схеме Hotel:")
                    for error in errors:
                        print(f"   - {error}")
                else:
                    print("✅ Схема Hotel корректна")
            
            # Выводим основную информацию
            if 'name' in data:
                print(f"   Название: {data['name']}")
            if 'description' in data:
                print(f"   Описание: {data['description'][:100]}...")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    base_url = input("Введите базовый URL сайта (например, http://localhost:8000): ").strip()
    
    if not base_url:
        base_url = "http://localhost:8000"
    
    # Тестируемые страницы
    test_pages = [
        "/",
        "/ru/",
        "/en/",
        "/kk/",
    ]
    
    print("🚀 Начинаем тестирование структурированных данных...")
    print(f"🌐 Базовый URL: {base_url}")
    
    results = []
    for page in test_pages:
        url = urljoin(base_url, page)
        success = test_page_structured_data(url)
        results.append((url, success))
    
    # Сводка результатов
    print("\n" + "="*60)
    print("📊 СВОДКА РЕЗУЛЬТАТОВ")
    print("="*60)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for url, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {url}")
    
    print(f"\n📈 Успешно: {successful}/{total} страниц")
    
    if successful == total:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("⚠️  Некоторые тесты провалились. Проверьте структурированные данные.")

if __name__ == "__main__":
    main() 