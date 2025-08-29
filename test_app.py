#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы EduVerse без WebSocket
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app_simple import app, db, User, School
    
    print("✅ Импорт модулей успешен")
    
    # Создаем контекст приложения
    with app.app_context():
        print("✅ Контекст приложения создан")
        
        # Проверяем создание таблиц
        db.create_all()
        print("✅ Таблицы базы данных созданы")
        
        # Проверяем создание супер-админа
        if not User.query.filter_by(role='super_admin').first():
            from werkzeug.security import generate_password_hash
            super_admin = User(
                username='admin',
                email='admin@eduverse.com',
                password_hash=generate_password_hash('admin123'),
                role='super_admin'
            )
            db.session.add(super_admin)
            db.session.commit()
            print("✅ Супер-админ создан: admin / admin123")
        else:
            print("✅ Супер-админ уже существует")
        
        # Проверяем количество пользователей
        user_count = User.query.count()
        print(f"✅ Количество пользователей в базе: {user_count}")
        
        # Проверяем маршруты
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        print(f"✅ Доступные маршруты: {len(routes)}")
        for route in routes[:5]:  # Показываем первые 5 маршрутов
            print(f"   - {route}")
        
        print("\n🎉 Все тесты пройдены успешно!")
        print("🚀 Приложение готово к запуску на порту 5001")
        print("📱 Используйте: python3 app_simple.py")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)