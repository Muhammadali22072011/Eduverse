from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for all platform users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    schools = db.relationship('School', back_populates='owner', cascade='all, delete-orphan')
    grades = db.relationship('Grade', back_populates='teacher', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='student', cascade='all, delete-orphan')
    chat_participants = db.relationship('ChatParticipant', back_populates='user', cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', back_populates='sender', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    materials = db.relationship('Material', back_populates='uploader', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    def has_role(self, role_name):
        """Check if user has specific role"""
        return any(role.role.name == role_name for role in self.roles)
    
    def get_primary_role(self):
        """Get user's primary role (highest priority)"""
        if not self.roles:
            return None
        return max(self.roles, key=lambda x: x.role.priority)
    
    def get_schools(self):
        """Get all schools user is associated with"""
        schools = []
        for role in self.roles:
            if role.school:
                schools.append(role.school)
        return list(set(schools))
    
    def __repr__(self):
        return f'<User {self.username}>'