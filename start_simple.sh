#!/bin/bash

echo "🚀 Запуск EduVerse без WebSocket..."

# Убиваем все существующие процессы Python
echo "🧹 Очистка старых процессов..."
pkill -f "python3.*app_simple" 2>/dev/null || true
sleep 2

# Запускаем приложение
echo "▶️  Запуск приложения..."
python3 app_simple_fixed.py &

# Ждем запуска
echo "⏳ Ожидание запуска..."
sleep 5

# Проверяем статус
echo "🔍 Проверка статуса..."
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ Приложение успешно запущено!"
    echo "🌐 URL: http://localhost:5001"
    echo "🔑 Логин: admin / admin123"
    echo "📊 База данных: eduverse_simple.db"
    echo ""
    echo "Для остановки: pkill -f 'python3.*app_simple'"
else
    echo "❌ Приложение не запустилось"
    echo "Проверьте логи выше"
fi