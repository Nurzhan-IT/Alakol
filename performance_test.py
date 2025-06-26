#!/usr/bin/env python3
"""
Скрипт для тестирования производительности Django приложения Alakol
Использование: python performance_test.py [host] [port]
"""

import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor
import argparse
import sys

class PerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.errors = []
        
    def test_endpoint(self, endpoint, timeout=30):
        """Тестирует один endpoint и возвращает время отклика"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=timeout)
            end_time = time.time()
            
            response_time = end_time - start_time
            return {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200
            }
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'status_code': 0,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e)
            }
    
    def concurrent_test(self, endpoint, num_requests=100, concurrent_users=10):
        """Выполняет конкурентное тестирование endpoint"""
        print(f"Тестирование {endpoint} с {num_requests} запросами и {concurrent_users} одновременными пользователями...")
        
        results = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(self.test_endpoint, endpoint) for _ in range(num_requests)]
            
            for future in futures:
                result = future.result()
                results.append(result)
                if not result['success']:
                    self.errors.append(result)
        
        return results
    
    def analyze_results(self, results):
        """Анализирует результаты тестирования"""
        if not results:
            return None
            
        successful_results = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in successful_results]
        
        if not response_times:
            return {
                'total_requests': len(results),
                'successful_requests': 0,
                'failed_requests': len(results),
                'success_rate': 0,
                'error': 'Все запросы завершились ошибкой'
            }
        
        total_time = sum(response_times)
        
        analysis = {
            'total_requests': len(results),
            'successful_requests': len(successful_results),
            'failed_requests': len(results) - len(successful_results),
            'success_rate': len(successful_results) / len(results) * 100,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'median_response_time': statistics.median(response_times),
            'requests_per_second': len(successful_results) / total_time if total_time > 0 else 0
        }
        
        if len(response_times) > 1:
            analysis['std_deviation'] = statistics.stdev(response_times)
        
        return analysis
    
    def run_comprehensive_test(self):
        """Запускает комплексное тестирование всех основных endpoint'ов"""
        endpoints = [
            '/',                    # Главная страница
            '/admin/',             # Админка (может быть недоступна без авторизации)
        ]
        
        # Дополнительные endpoints, если известны
        # Можно добавить реальные URL вашего приложения
        
        print("🚀 Начинаем комплексное тестирование производительности...")
        print("=" * 60)
        
        all_results = {}
        
        for endpoint in endpoints:
            print(f"\n📊 Тестирование endpoint: {endpoint}")
            results = self.concurrent_test(endpoint, num_requests=50, concurrent_users=5)
            analysis = self.analyze_results(results)
            all_results[endpoint] = analysis
            
            if analysis:
                self.print_analysis(endpoint, analysis)
            else:
                print(f"❌ Не удалось получить результаты для {endpoint}")
        
        print("\n" + "=" * 60)
        print("📋 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        
        total_rps = 0
        total_avg_time = 0
        working_endpoints = 0
        
        for endpoint, analysis in all_results.items():
            if analysis and analysis.get('requests_per_second', 0) > 0:
                total_rps += analysis['requests_per_second']
                total_avg_time += analysis['avg_response_time']
                working_endpoints += 1
                print(f"{endpoint:20} | RPS: {analysis['requests_per_second']:6.1f} | Время: {analysis['avg_response_time']*1000:6.1f}ms")
        
        if working_endpoints > 0:
            avg_rps = total_rps / working_endpoints
            avg_time = total_avg_time / working_endpoints
            
            print("\n🎯 ОБЩИЕ МЕТРИКИ:")
            print(f"   Средний RPS: {avg_rps:.1f}")
            print(f"   Среднее время отклика: {avg_time*1000:.1f}ms")
            print(f"   Работающих endpoints: {working_endpoints}/{len(endpoints)}")
            
            # Оценка производительности
            if avg_rps >= 50:
                performance_rating = "🟢 Отличная"
            elif avg_rps >= 20:
                performance_rating = "🟡 Хорошая"
            elif avg_rps >= 10:
                performance_rating = "🟠 Удовлетворительная"
            else:
                performance_rating = "🔴 Требует оптимизации"
                
            print(f"   Оценка производительности: {performance_rating}")
        
        if self.errors:
            print(f"\n❌ Обнаружено ошибок: {len(self.errors)}")
            for error in self.errors[:5]:  # Показываем первые 5 ошибок
                print(f"   {error['endpoint']}: {error.get('error', 'Unknown error')}")
    
    def print_analysis(self, endpoint, analysis):
        """Выводит анализ результатов для endpoint"""
        print(f"✅ Результаты для {endpoint}:")
        print(f"   📈 RPS: {analysis['requests_per_second']:.2f}")
        print(f"   ⏱️  Среднее время отклика: {analysis['avg_response_time']*1000:.2f}ms")
        print(f"   ✅ Успешных запросов: {analysis['successful_requests']}/{analysis['total_requests']} ({analysis['success_rate']:.1f}%)")
        print(f"   📊 Мин/Макс время: {analysis['min_response_time']*1000:.2f}ms / {analysis['max_response_time']*1000:.2f}ms")

def main():
    parser = argparse.ArgumentParser(description='Тестирование производительности Django приложения')
    parser.add_argument('--host', default='localhost', help='Хост для тестирования (по умолчанию: localhost)')
    parser.add_argument('--port', default='8000', help='Порт для тестирования (по умолчанию: 8000)')
    parser.add_argument('--endpoint', help='Конкретный endpoint для тестирования (например: /)')
    parser.add_argument('--requests', type=int, default=100, help='Количество запросов (по умолчанию: 100)')
    parser.add_argument('--concurrent', type=int, default=10, help='Количество одновременных пользователей (по умолчанию: 10)')
    
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    tester = PerformanceTester(base_url)
    
    print(f"🔍 Тестирование сервера: {base_url}")
    
    # Проверяем доступность сервера
    try:
        response = requests.get(base_url, timeout=10)
        print(f"✅ Сервер доступен (статус: {response.status_code})")
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        print("💡 Убедитесь, что Django сервер запущен командой: python manage.py runserver")
        sys.exit(1)
    
    if args.endpoint:
        # Тестируем конкретный endpoint
        print(f"\n🎯 Тестирование endpoint: {args.endpoint}")
        results = tester.concurrent_test(args.endpoint, args.requests, args.concurrent)
        analysis = tester.analyze_results(results)
        if analysis:
            tester.print_analysis(args.endpoint, analysis)
    else:
        # Комплексное тестирование
        tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 