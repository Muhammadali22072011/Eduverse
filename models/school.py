from datetime import datetime
from .user import db

class School(db.Model):
    """School model for educational institutions"""
    __tablename__ = 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)  # For URL routing
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    logo = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    owner = db.relationship('User', back_populates='schools')
    settings = db.relationship('SchoolSettings', back_populates='school', uselist=False, cascade='all, delete-orphan')
    user_roles = db.relationship('UserRole', back_populates='school', cascade='all, delete-orphan')
    subjects = db.relationship('Subject', back_populates='school', cascade='all, delete-orphan')
    class_groups = db.relationship('ClassGroup', back_populates='school', cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', back_populates='school', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='school', cascade='all, delete-orphan')
    chats = db.relationship('Chat', back_populates='school', cascade='all, delete-orphan')
    materials = db.relationship('Material', back_populates='school', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<School {self.name}>'
    
    def get_url(self):
        """Get school URL"""
        return f"/school/{self.slug}"
    
    def get_admin_users(self):
        """Get all admin users for this school"""
        from .role import UserRole
        return UserRole.query.filter_by(
            school_id=self.id,
            role_id=Role.query.filter_by(name='school_admin').first().id
        ).all()

class SchoolSettings(db.Model):
    """School-specific settings and configuration"""
    __tablename__ = 'school_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
    # General settings
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='ru')
    currency = db.Column(db.String(3), default='RUB')
    
    # Academic settings
    academic_year_start = db.Column(db.Date)
    academic_year_end = db.Column(db.Date)
    grading_system = db.Column(db.String(20), default='10-point')  # 10-point, 5-point, etc.
    auto_student_assignment = db.Column(db.Boolean, default=True)
    assignment_mode = db.Column(db.String(20), default='by_class')  # by_class, by_subject
    
    # Payment settings
    payment_due_day = db.Column(db.Integer, default=15)  # Day of month
    payment_reminder_days = db.Column(db.Integer, default=7)
    late_fee_percentage = db.Column(db.Float, default=0.0)
    
    # Chat settings
    chat_enabled = db.Column(db.Boolean, default=True)
    chat_moderation = db.Column(db.Boolean, default=True)
    chat_archiving_days = db.Column(db.Integer, default=365)
    
    # Notification settings
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = db.relationship('School', back_populates='settings')
    
    def __repr__(self):
        return f'<SchoolSettings {self.school.name}>'