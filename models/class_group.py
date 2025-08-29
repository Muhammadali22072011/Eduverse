from datetime import datetime
from .user import db

class ClassGroup(db.Model):
    """Class group model for organizing students"""
    __tablename__ = 'class_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g., "5A", "10Б"
    description = db.Column(db.Text)
    academic_year = db.Column(db.String(9))  # e.g., "2024-2025"
    max_students = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    school = db.relationship('School', back_populates='class_groups')
    student_classes = db.relationship('StudentClass', back_populates='class_group', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ClassGroup {self.name}>'
    
    def get_student_count(self):
        """Get current number of students in class"""
        return len([sc for sc in self.student_classes if sc.is_active])

class StudentClass(db.Model):
    """Many-to-many relationship between students and class groups"""
    __tablename__ = 'student_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id])
    class_group = db.relationship('ClassGroup', back_populates='student_classes')
    
    def __repr__(self):
        return f'<StudentClass {self.student.username} -> {self.class_group.name}>'