from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Инициализация Flask приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduverse_minimal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Простые модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password_hash == password:  # Упрощенная проверка для тестирования
            flash('Вход выполнен успешно!')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=password,  # Упрощено для тестирования
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/super-admin-dashboard')
def super_admin_dashboard():
    schools = School.query.all()
    stats = {
        'total_schools': len(schools),
        'total_users': User.query.count(),
        'active_schools': len([s for s in schools if s.created_at]),
        'total_revenue': 0
    }
    
    return render_template('super_admin_dashboard.html', 
                         schools=schools, 
                         stats=stats,
                         recent_activities=[])

@app.route('/student-dashboard')
def student_dashboard():
    stats = {
        'average_grade': 'N/A',
        'subjects_count': 0,
        'attendance_percent': 0,
        'homework_count': 0
    }
    
    return render_template('student_dashboard.html', 
                         stats=stats,
                         today_schedule=[],
                         recent_grades=[],
                         homework=[],
                         notifications=[],
                         materials=[])

# API маршруты
@app.route('/api/schools', methods=['GET'])
def get_schools():
    schools = School.query.all()
    return jsonify([{
        'id': school.id,
        'name': school.name,
        'description': school.description
    } for school in schools])

@app.route('/api/schools', methods=['POST'])
def create_school():
    data = request.get_json()
    school = School(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(school)
    db.session.commit()
    
    return jsonify({'id': school.id, 'message': 'Школа создана успешно'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Создание супер-админа по умолчанию
        if not User.query.filter_by(role='super_admin').first():
            super_admin = User(
                username='admin',
                email='admin@eduverse.com',
                password_hash='admin123',
                role='super_admin'
            )
            db.session.add(super_admin)
            db.session.commit()
            print("Супер-админ создан: admin / admin123")
    
    print("🚀 EduVerse (минимальная версия) запущен на http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)