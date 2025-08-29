#!/usr/bin/env python3
"""
Простое тестовое Flask приложение
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>EduVerse Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #4CAF50; color: white; padding: 20px; border-radius: 5px; }
            .content { padding: 20px; background: #f9f9f9; margin-top: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EduVerse - Тестовая версия</h1>
                <p>Простое Flask приложение без WebSocket</p>
            </div>
            <div class="content">
                <h2>✅ Приложение работает!</h2>
                <p>Это минимальная версия EduVerse без WebSocket функциональности.</p>
                <ul>
                    <li>Flask: Работает</li>
                    <li>SQLAlchemy: Готов к использованию</li>
                    <li>WebSocket: Отключен</li>
                </ul>
                <h3>Следующие шаги:</h3>
                <p>Теперь вы можете:</p>
                <ol>
                    <li>Добавить аутентификацию</li>
                    <li>Создать модели базы данных</li>
                    <li>Добавить API endpoints</li>
                    <li>Создать веб-интерфейс</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/api/status')
def status():
    return {'status': 'ok', 'message': 'EduVerse работает без WebSocket'}

if __name__ == '__main__':
    print("🚀 Запуск простого тестового приложения на http://localhost:9000")
    app.run(debug=True, host='0.0.0.0', port=9000)