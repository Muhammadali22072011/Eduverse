#!/usr/bin/env python3
"""
Минимальный тест Flask приложения
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, EduVerse!'

@app.route('/test')
def test():
    return 'Test endpoint works!'

if __name__ == '__main__':
    print("🚀 Запуск минимального теста на порту 5002")
    app.run(debug=False, host='0.0.0.0', port=5002)