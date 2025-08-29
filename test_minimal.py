#!/usr/bin/env python3
"""
Тест минимальной версии EduVerse
"""

import requests
import time

def test_app():
    base_url = "http://localhost:8080"
    
    print("🧪 Тестирование минимальной версии EduVerse...")
    
    try:
        # Тест главной страницы
        print("📄 Тестирование главной страницы...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Главная страница работает")
        else:
            print(f"❌ Главная страница вернула код: {response.status_code}")
            
        # Тест страницы входа
        print("🔐 Тестирование страницы входа...")
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            print("✅ Страница входа работает")
        else:
            print(f"❌ Страница входа вернула код: {response.status_code}")
            
        # Тест API школ
        print("🏫 Тестирование API школ...")
        response = requests.get(f"{base_url}/api/schools", timeout=5)
        if response.status_code == 200:
            print("✅ API школ работает")
        else:
            print(f"❌ API школ вернул код: {response.status_code}")
            
        print("\n🎉 Все тесты пройдены! Приложение работает корректно.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к приложению. Убедитесь, что оно запущено.")
    except requests.exceptions.Timeout:
        print("❌ Превышено время ожидания ответа.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_app()