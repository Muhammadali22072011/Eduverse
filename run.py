#!/usr/bin/env python3
"""
Файл для запуска EduVerse в продакшене
Использует Gunicorn для production deployment
"""

import os
import sys
from app import app, socketio

if __name__ == '__main__':
    # Проверка переменных окружения
    if not os.getenv('SECRET_KEY'):
        print("ОШИБКА: SECRET_KEY не установлен!")
        print("Установите переменную окружения SECRET_KEY")
        sys.exit(1)
    
    # Настройки для продакшена
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Запуск EduVerse на {host}:{port}")
    print(f"🔧 Режим отладки: {'Включен' if debug else 'Отключен'}")
    
    try:
        # Запуск приложения
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            log_output=True
        )
    except KeyboardInterrupt:
        print("\n👋 EduVerse остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)