from datetime import datetime
from .user import db

class Subject(db.Model):
    """Subject model for educational subjects"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(20))  # Subject code like "MATH", "ENG"
    color = db.Column(db.String(7), default='#007bff')  # Hex color for UI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    school = db.relationship('School', back_populates='subjects')
    grades = db.relationship('Grade', back_populates='subject', cascade='all, delete-orphan')
    materials = db.relationship('Material', back_populates='subject', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subject {self.name}>'