from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Инициализация Flask приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Простые модели базы данных
class User(UserMixin, db.Model):
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

# Инициализация пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
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
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'super_admin':
        return redirect(url_for('super_admin_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    else:
        return redirect(url_for('index'))

@app.route('/super-admin-dashboard')
@login_required
def super_admin_dashboard():
    if current_user.role != 'super_admin':
        flash('Недостаточно прав')
        return redirect(url_for('dashboard'))
    
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
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Недостаточно прав')
        return redirect(url_for('dashboard'))
    
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
@login_required
def create_school():
    if current_user.role not in ['super_admin']:
        return jsonify({'error': 'Недостаточно прав'}), 403
    
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
                password_hash=generate_password_hash('admin123'),
                role='super_admin'
            )
            db.session.add(super_admin)
            db.session.commit()
            print("Супер-админ создан: admin / admin123")
    
    print("🚀 EduVerse запущен на http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)