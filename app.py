import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

from config import config
from models import db, User, Role, School, SchoolSettings

# Initialize Flask extensions
login_manager = LoginManager()
socketio = SocketIO()
migrate = Migrate()

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)
    CORS(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.school import school_bp
    from routes.admin import admin_bp
    from routes.chat import chat_bp
    from routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(school_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    return app

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        emit('status', {'msg': f'{current_user.username} подключился'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        emit('status', {'msg': f'{current_user.username} отключился'}, broadcast=True)

@socketio.on('join')
def handle_join(data):
    """Handle joining a room"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('status', {'msg': f'{current_user.username} присоединился к {room}'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    """Handle leaving a room"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('status', {'msg': f'{current_user.username} покинул {room}'}, room=room)

@socketio.on('message')
def handle_message(data):
    """Handle chat messages"""
    room = data.get('room')
    message = data.get('message')
    
    if room and message and current_user.is_authenticated:
        # Save message to database
        from models.chat import Chat, ChatMessage, ChatParticipant
        
        # Find or create chat
        chat = Chat.query.filter_by(id=room).first()
        if chat:
            # Check if user is participant
            participant = ChatParticipant.query.filter_by(
                user_id=current_user.id,
                chat_id=room
            ).first()
            
            if participant:
                # Create message
                chat_message = ChatMessage(
                    content=message,
                    sender_id=current_user.id,
                    chat_id=room
                )
                db.session.add(chat_message)
                chat.last_message_at = datetime.utcnow()
                db.session.commit()
                
                # Emit to room
                emit('message', {
                    'user': current_user.username,
                    'message': message,
                    'timestamp': chat_message.created_at.isoformat()
                }, room=room)
            else:
                emit('error', {'msg': 'У вас нет доступа к этому чату'})

def init_db():
    """Initialize database with default data"""
    # Create tables
    db.create_all()
    
    # Create default roles if they don't exist
    roles_data = [
        {'name': 'super_admin', 'description': 'Главный администратор платформы', 'priority': 100},
        {'name': 'project_admin', 'description': 'Администратор проекта', 'priority': 90},
        {'name': 'school_admin', 'description': 'Администратор школы', 'priority': 80},
        {'name': 'teacher', 'description': 'Учитель', 'priority': 70},
        {'name': 'student', 'description': 'Ученик', 'priority': 60},
        {'name': 'parent', 'description': 'Родитель', 'priority': 50}
    ]
    
    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
    
    # Create super admin user if it doesn't exist
    super_admin = User.query.filter_by(username='admin').first()
    if not super_admin:
        super_admin = User(
            username='admin',
            email='admin@eduverse.com',
            password='admin123',
            first_name='Администратор',
            last_name='Системы',
            is_verified=True
        )
        db.session.add(super_admin)
        db.session.flush()  # Get the ID
        
        # Assign super admin role
        from models.role import UserRole
        super_admin_role = Role.query.filter_by(name='super_admin').first()
        if super_admin_role:
            user_role = UserRole(
                user_id=super_admin.id,
                role_id=super_admin_role.id
            )
            db.session.add(user_role)
    
    db.session.commit()
    print("Database initialized successfully!")

if __name__ == '__main__':
    app = create_app()
    
    # Initialize database
    init_db()
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)