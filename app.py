from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import uuid

# Инициализация Flask приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Модели базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # super_admin, project_admin, school_admin, teacher, student, parent
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи будут определены после всех моделей

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    unique_url = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(200))
    contact_info = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    description = db.Column(db.Text)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    grade_level = db.Column(db.Integer, nullable=False)

class TeacherSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class StudentSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class ClassStudent(db.Model):
    __tablename__ = 'class_student'
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)  # 1-10 баллов
    date = db.Column(db.Date, nullable=False)
    comment = db.Column(db.Text)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (понедельник-воскресенье)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.String(50))  # exam, holiday, event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='due')  # paid, partial, due
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

class ParentChild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    chat_type = db.Column(db.String(20), nullable=False)  # private, group
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatParticipant(db.Model):
    __tablename__ = 'chat_participant'
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_pinned = db.Column(db.Boolean, default=False)

# Определение связей после всех моделей
def setup_relationships():
    # User relationships
    User.school = db.relationship('School', backref='users')
    User.teacher_subjects = db.relationship('TeacherSubject', backref='teacher')
    User.student_subjects = db.relationship('StudentSubject', backref='student')
    User.grades = db.relationship('Grade', backref='student')
    User.payments = db.relationship('Payment', backref='student')
    User.parent_children = db.relationship('ParentChild', foreign_keys='ParentChild.parent_id', backref='parent')
    User.sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    User.received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')
    
    # School relationships
    School.subjects = db.relationship('Subject', backref='school')
    School.classes = db.relationship('Class', backref='school')
    School.schedules = db.relationship('Schedule', backref='school')
    School.events = db.relationship('Event', backref='school')
    
    # Subject relationships
    Subject.teacher_subjects = db.relationship('TeacherSubject', backref='subject')
    Subject.student_subjects = db.relationship('StudentSubject', backref='student')
    Subject.grades = db.relationship('Grade', backref='subject')
    
    # Class relationships
    Class.students = db.relationship('User', secondary='class_student')
    
    # Chat relationships
    Chat.participants = db.relationship('User', secondary='chat_participant')
    Chat.messages = db.relationship('Message', backref='chat')

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
    elif current_user.role == 'project_admin':
        return redirect(url_for('project_admin_dashboard'))
    elif current_user.role == 'school_admin':
        return redirect(url_for('school_admin_dashboard'))
    elif current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    elif current_user.role == 'parent':
        return redirect(url_for('parent_dashboard'))
    
    return redirect(url_for('index'))

# API маршруты для школ
@app.route('/api/schools', methods=['GET'])
def get_schools():
    schools = School.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': school.id,
        'name': school.name,
        'unique_url': school.unique_url,
        'description': school.description
    } for school in schools])

@app.route('/api/schools', methods=['POST'])
@login_required
def create_school():
    if current_user.role not in ['super_admin', 'project_admin']:
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    data = request.get_json()
    school = School(
        name=data['name'],
        unique_url=data['unique_url'],
        description=data.get('description', ''),
        contact_info=data.get('contact_info', '')
    )
    db.session.add(school)
    db.session.commit()
    
    return jsonify({'id': school.id, 'message': 'Школа создана успешно'})

# Socket.IO события для чата
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'Пользователь присоединился к чату {room}'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'Пользователь покинул чат {room}'}, room=room)

@socketio.on('message')
def on_message(data):
    room = data['room']
    emit('message', data, room=room)

if __name__ == '__main__':
    with app.app_context():
        # Настройка связей между моделями
        setup_relationships()
        
        # Создание таблиц
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
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)