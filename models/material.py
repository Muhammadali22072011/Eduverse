from datetime import datetime
from .user import db

class Material(db.Model):
    """Material model for educational resources"""
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    material_type = db.Column(db.String(50), default='document')  # document, video, audio, link, etc.
    
    # File information
    file_url = db.Column(db.String(500))
    file_name = db.Column(db.String(200))
    file_size = db.Column(db.Integer)  # Size in bytes
    file_extension = db.Column(db.String(20))
    mime_type = db.Column(db.String(100))
    
    # Access settings
    is_public = db.Column(db.Boolean, default=False)
    requires_auth = db.Column(db.Boolean, default=True)
    download_count = db.Column(db.Integer, default=0)
    
    # Academic context
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'))
    
    # Metadata
    tags = db.Column(db.JSON)  # Store tags as JSON array
    language = db.Column(db.String(10), default='ru')
    version = db.Column(db.String(20), default='1.0')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    uploader = db.relationship('User', back_populates='materials', foreign_keys=[uploader_id])
    school = db.relationship('School', back_populates='materials')
    subject = db.relationship('Subject', back_populates='materials')
    class_group = db.relationship('ClassGroup')
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def __repr__(self):
        return f'<Material {self.title} by {self.uploader.username}>'
    
    def get_file_size_mb(self):
        """Get file size in megabytes"""
        if not self.file_size:
            return 0
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_file_size_formatted(self):
        """Get human-readable file size"""
        if not self.file_size:
            return "0 B"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_download_url(self):
        """Get download URL for material"""
        if self.file_url:
            return self.file_url
        return f"/materials/{self.id}/download"
    
    def can_download(self, user):
        """Check if user can download this material"""
        if not self.is_active:
            return False
        
        if not self.requires_auth:
            return True
        
        if not user.is_authenticated:
            return False
        
        # Check if user has access to the school
        if user.has_role('super_admin') or user.has_role('project_admin'):
            return True
        
        # Check if user is in the same school
        user_schools = user.get_schools()
        if any(school.id == self.school_id for school in user_schools):
            return True
        
        return False
    
    def increment_download_count(self):
        """Increment download counter"""
        self.download_count += 1
    
    def get_icon_class(self):
        """Get icon class based on material type"""
        icons = {
            'document': 'fas fa-file-alt',
            'pdf': 'fas fa-file-pdf',
            'video': 'fas fa-video',
            'audio': 'fas fa-music',
            'image': 'fas fa-image',
            'link': 'fas fa-link',
            'presentation': 'fas fa-presentation',
            'spreadsheet': 'fas fa-table'
        }
        return icons.get(self.material_type, 'fas fa-file')
    
    def get_type_display_name(self):
        """Get human-readable material type name"""
        type_names = {
            'document': 'Документ',
            'pdf': 'PDF документ',
            'video': 'Видео',
            'audio': 'Аудио',
            'image': 'Изображение',
            'link': 'Ссылка',
            'presentation': 'Презентация',
            'spreadsheet': 'Таблица'
        }
        return type_names.get(self.material_type, 'Файл')