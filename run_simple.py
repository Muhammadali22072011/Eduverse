#!/usr/bin/env python3
"""
Файл для запуска EduVerse без WebSocket функциональности
Использует стандартный Flask без SocketIO
"""

import os
import sys
from app_simple import app

if __name__ == '__main__':
    # Проверка переменных окружения
    if not os.getenv('SECRET_KEY'):
        print("⚠️  SECRET_KEY не установлен, используется значение по умолчанию")
        print("Для продакшена установите переменную окружения SECRET_KEY")
    
    # Настройки для запуска
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Запуск EduVerse (без WebSocket) на {host}:{port}")
    print(f"🔧 Режим отладки: {'Включен' if debug else 'Отключен'}")
    print(f"📱 Доступно по адресу: http://localhost:{port}")
    
    try:
        # Запуск приложения
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n👋 EduVerse остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)