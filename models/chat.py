from datetime import datetime
from .user import db

class Chat(db.Model):
    """Chat model for communication between users"""
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    chat_type = db.Column(db.String(20), default='private')  # private, group, subject, class
    description = db.Column(db.Text)
    
    # Chat settings
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    allow_attachments = db.Column(db.Boolean, default=True)
    require_moderation = db.Column(db.Boolean, default=False)
    
    # Academic context
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = db.Column(db.DateTime)
    
    # Relationships
    school = db.relationship('School', back_populates='chats')
    subject = db.relationship('Subject')
    class_group = db.relationship('ClassGroup')
    participants = db.relationship('ChatParticipant', back_populates='chat', cascade='all, delete-orphan')
    messages = db.relationship('ChatMessage', back_populates='chat', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Chat {self.name or self.id}>'
    
    def get_display_name(self):
        """Get display name for chat"""
        if self.name:
            return self.name
        elif self.subject:
            return f"Чат по предмету: {self.subject.name}"
        elif self.class_group:
            return f"Чат класса: {self.class_group.name}"
        else:
            return f"Чат #{self.id}"
    
    def get_participant_count(self):
        """Get number of active participants"""
        return len([p for p in self.participants if p.is_active])

class ChatParticipant(db.Model):
    """Many-to-many relationship between users and chats"""
    __tablename__ = 'chat_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    
    # Participant settings
    role = db.Column(db.String(20), default='member')  # member, moderator, admin
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime)
    
    # Notification settings
    notifications_enabled = db.Column(db.Boolean, default=True)
    last_read_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='chat_participants')
    chat = db.relationship('Chat', back_populates='participants')
    
    def __repr__(self):
        return f'<ChatParticipant {self.user.username} in {self.chat.get_display_name()}>'
    
    def get_unread_count(self):
        """Get number of unread messages"""
        if not self.last_read_at:
            return ChatMessage.query.filter_by(chat_id=self.chat_id).count()
        
        return ChatMessage.query.filter(
            ChatMessage.chat_id == self.chat_id,
            ChatMessage.created_at > self.last_read_at
        ).count()

class ChatMessage(db.Model):
    """Individual chat messages"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    
    # Message metadata
    is_edited = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    
    # File attachments
    attachment_url = db.Column(db.String(500))
    attachment_name = db.Column(db.String(200))
    attachment_size = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'))
    
    # Relationships
    sender = db.relationship('User', back_populates='chat_messages')
    chat = db.relationship('Chat', back_populates='messages')
    reply_to = db.relationship('ChatMessage', remote_side=[id])
    
    def __repr__(self):
        return f'<ChatMessage {self.id} from {self.sender.username}>'
    
    def is_system_message(self):
        """Check if message is a system message"""
        return self.message_type == 'system'
    
    def can_edit(self, user):
        """Check if user can edit this message"""
        return (user.id == self.sender_id and 
                not self.is_deleted and 
                (datetime.utcnow() - self.created_at).total_seconds() < 300)  # 5 minutes
    
    def can_delete(self, user):
        """Check if user can delete this message"""
        return (user.id == self.sender_id or 
                user.has_role('school_admin') or 
                user.has_role('super_admin'))