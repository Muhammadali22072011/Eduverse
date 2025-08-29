from datetime import datetime
from .user import db

class Grade(db.Model):
    """Grade model for student academic performance"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=False)  # 1-10 scale
    comment = db.Column(db.Text)
    grade_type = db.Column(db.String(50), default='regular')  # regular, test, exam, homework
    
    # Academic context
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Date and time
    date_given = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', back_populates='grades')
    student = db.relationship('User', foreign_keys=[student_id])
    teacher = db.relationship('User', foreign_keys=[teacher_id], back_populates='grades')
    
    def __repr__(self):
        return f'<Grade {self.grade} for {self.student.username} in {self.subject.name}>'
    
    def is_passing(self):
        """Check if grade is passing (5 or higher)"""
        return self.grade >= 5
    
    def get_grade_letter(self):
        """Get grade as letter (for display purposes)"""
        grade_letters = {
            10: 'A+', 9: 'A', 8: 'B+', 7: 'B', 6: 'C+',
            5: 'C', 4: 'D+', 3: 'D', 2: 'F+', 1: 'F'
        }
        return grade_letters.get(self.grade, str(self.grade))
    
    def get_grade_color(self):
        """Get color for grade display"""
        if self.grade >= 8:
            return 'success'  # Green
        elif self.grade >= 6:
            return 'warning'  # Yellow
        else:
            return 'danger'   # Red