#!/usr/bin/env python3
"""
Простой тест для проверки работы Flask приложения
"""

import requests
import time

def test_app():
    base_url = "http://localhost:5001"
    
    print("🧪 Тестирование EduVerse приложения...")
    print(f"📍 URL: {base_url}")
    
    try:
        # Тест главной страницы
        print("\n1️⃣ Тестирование главной страницы...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Главная страница загружается успешно")
            print(f"   Размер ответа: {len(response.text)} символов")
        else:
            print(f"❌ Ошибка главной страницы: {response.status_code}")
            
        # Тест страницы входа
        print("\n2️⃣ Тестирование страницы входа...")
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            print("✅ Страница входа загружается успешно")
        else:
            print(f"❌ Ошибка страницы входа: {response.status_code}")
            
        # Тест страницы регистрации
        print("\n3️⃣ Тестирование страницы регистрации...")
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code == 200:
            print("✅ Страница регистрации загружается успешно")
        else:
            print(f"❌ Ошибка страницы регистрации: {response.status_code}")
            
        # Тест API школ
        print("\n4️⃣ Тестирование API школ...")
        response = requests.get(f"{base_url}/api/schools", timeout=5)
        if response.status_code == 200:
            print("✅ API школ работает успешно")
            try:
                schools = response.json()
                print(f"   Количество школ: {len(schools)}")
            except:
                print("   Ответ не является JSON")
        else:
            print(f"❌ Ошибка API школ: {response.status_code}")
            
        print("\n🎉 Тестирование завершено!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к приложению")
        print("   Убедитесь, что приложение запущено на порту 5001")
    except requests.exceptions.Timeout:
        print("❌ Таймаут при подключении")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_app()