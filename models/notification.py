from datetime import datetime
from .user import db

class Notification(db.Model):
    """Notification model for user alerts and messages"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')  # info, warning, error, success
    
    # Notification settings
    is_read = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    requires_action = db.Column(db.Boolean, default=False)
    
    # Action settings
    action_url = db.Column(db.String(500))  # URL to navigate to when clicked
    action_text = db.Column(db.String(100))  # Text for action button
    
    # Delivery settings
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)
    push_sent = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who sent the notification
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    
    # Relationships
    user = db.relationship('User', back_populates='notifications', foreign_keys=[user_id])
    sender = db.relationship('User', foreign_keys=[sender_id])
    school = db.relationship('School')
    
    def __repr__(self):
        return f'<Notification {self.title} for {self.user.username}>'
    
    def is_expired(self):
        """Check if notification has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def get_priority_class(self):
        """Get CSS class for notification priority"""
        if self.is_important:
            return 'notification-important'
        elif self.requires_action:
            return 'notification-action'
        else:
            return 'notification-info'
    
    def get_icon_class(self):
        """Get icon class based on notification type"""
        icons = {
            'info': 'fas fa-info-circle',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle',
            'success': 'fas fa-check-circle'
        }
        return icons.get(self.notification_type, 'fas fa-bell')
    
    def get_time_ago(self):
        """Get human-readable time ago string"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} дн. назад"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ч. назад"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} мин. назад"
        else:
            return "Только что"