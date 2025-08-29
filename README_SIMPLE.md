# EduVerse - Простая версия без WebSocket

## 🎯 Описание

Это упрощенная версия EduVerse, которая работает без WebSocket функциональности. Приложение использует только стандартный Flask без SocketIO, что решает проблемы совместимости с eventlet и SSL.

## ✨ Возможности

- ✅ Аутентификация пользователей (Flask-Login)
- ✅ Управление ролями (super_admin, student, teacher, etc.)
- ✅ Управление школами
- ✅ База данных SQLite
- ✅ REST API
- ✅ Веб-интерфейс
- ❌ WebSocket чат (отключен)

## 🚀 Быстрый запуск

### 1. Установка зависимостей

```bash
pip3 install --break-system-packages flask flask-sqlalchemy flask-login flask-wtf flask-migrate flask-cors wtforms email-validator
```

### 2. Запуск приложения

**Вариант 1: Прямой запуск**
```bash
python3 app_simple_fixed.py
```

**Вариант 2: Через скрипт (рекомендуется)**
```bash
chmod +x start_simple.sh
./start_simple.sh
```

**Вариант 3: Через run_simple.py**
```bash
python3 run_simple.py
```

### 3. Доступ к приложению

- 🌐 **URL**: http://localhost:5001
- 🔑 **Логин по умолчанию**: admin / admin123
- 📊 **База данных**: eduverse_simple.db

## 📁 Структура файлов

```
├── app_simple_fixed.py      # Основное приложение (без WebSocket)
├── run_simple.py            # Скрипт запуска
├── start_simple.sh          # Bash скрипт запуска
├── requirements_simple.txt   # Упрощенные зависимости
├── templates/               # HTML шаблоны
├── static/                  # CSS, JS, изображения
└── README_SIMPLE.md         # Этот файл
```

## 🔧 Конфигурация

### Порт
По умолчанию приложение запускается на порту **5001** (чтобы избежать конфликтов с портом 5000).

### База данных
- **Файл**: `eduverse_simple.db`
- **Тип**: SQLite
- **Автоматическое создание**: Да

### Переменные окружения
```bash
export PORT=5001          # Порт (по умолчанию: 5001)
export HOST=0.0.0.0      # Хост (по умолчанию: 0.0.0.0)
export DEBUG=True         # Режим отладки (по умолчанию: True)
export SECRET_KEY=your-key # Секретный ключ (опционально)
```

## 🧪 Тестирование

### Проверка работоспособности
```bash
curl http://localhost:5001/health
```

### Тест основных страниц
```bash
curl http://localhost:5001/           # Главная страница
curl http://localhost:5001/login      # Страница входа
curl http://localhost:5001/register   # Страница регистрации
```

### Тест API
```bash
curl http://localhost:5001/api/schools  # Список школ
```

## 🛠️ Устранение неполадок

### Порт занят
Если порт 5001 занят, измените его в файле `app_simple_fixed.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5002)  # Измените на 5002
```

### Процессы не запускаются
```bash
# Убить все процессы Python
pkill -f "python3.*app_simple"

# Очистить порты
sudo netstat -tulpn | grep :5001
```

### Проблемы с зависимостями
```bash
# Переустановить Flask
pip3 install --break-system-packages --force-reinstall flask

# Проверить версии
python3 -c "import flask; print(flask.__version__)"
```

## 📱 Использование

### 1. Откройте браузер
Перейдите по адресу: http://localhost:5001

### 2. Войдите в систему
- **Логин**: admin
- **Пароль**: admin123

### 3. Управление школами
- Создавайте новые школы
- Просматривайте статистику
- Управляйте пользователями

## 🔒 Безопасность

- ⚠️ **Только для разработки**: Не используйте в продакшене
- 🔑 **Секретный ключ**: Измените SECRET_KEY в продакшене
- 🚫 **Отладка**: Отключите debug=True в продакшене
- 🌐 **Хост**: Ограничьте доступ в продакшене

## 📈 Развитие

### Добавление новых функций
1. Создайте новые модели в `app_simple_fixed.py`
2. Добавьте маршруты
3. Создайте HTML шаблоны
4. Обновите базу данных

### Миграции базы данных
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи приложения
2. Убедитесь, что все зависимости установлены
3. Проверьте, что порт 5001 свободен
4. Убедитесь, что у вас есть права на запись в директорию

## 🎉 Готово!

Теперь у вас есть работающая версия EduVerse без WebSocket! Приложение полностью функционально и готово к использованию и дальнейшей разработке.