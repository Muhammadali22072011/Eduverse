from datetime import datetime, date
from .user import db

class Payment(db.Model):
    """Payment model for student financial tracking"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Payment amount
    currency = db.Column(db.String(3), default='RUB')
    
    # Payment details
    payment_type = db.Column(db.String(50), default='tuition')  # tuition, materials, events, etc.
    description = db.Column(db.Text)
    invoice_number = db.Column(db.String(50))
    
    # Payment status
    status = db.Column(db.String(20), default='pending')  # pending, paid, partial, overdue, cancelled
    paid_amount = db.Column(db.Numeric(10, 2), default=0)  # Amount actually paid
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date)
    
    # Academic context
    month = db.Column(db.Integer)  # Month for monthly payments (1-12)
    year = db.Column(db.Integer)   # Year for payments
    academic_year = db.Column(db.String(9))  # Academic year
    
    # Relationships
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', back_populates='payments')
    school = db.relationship('School', back_populates='payments')
    
    def __repr__(self):
        return f'<Payment {self.amount} {self.currency} for {self.student.username}>'
    
    def get_remaining_amount(self):
        """Get remaining amount to be paid"""
        return float(self.amount - self.paid_amount)
    
    def get_payment_percentage(self):
        """Get percentage of payment completed"""
        if self.amount == 0:
            return 0
        return (float(self.paid_amount) / float(self.amount)) * 100
    
    def is_overdue(self):
        """Check if payment is overdue"""
        return self.due_date < date.today() and self.status != 'paid'
    
    def is_partial(self):
        """Check if payment is partially paid"""
        return self.paid_amount > 0 and self.paid_amount < self.amount
    
    def get_status_color(self):
        """Get color for payment status display"""
        if self.status == 'paid':
            return 'success'  # Green
        elif self.status == 'partial':
            return 'warning'  # Yellow
        elif self.is_overdue():
            return 'danger'   # Red
        else:
            return 'info'     # Blue
    
    def get_status_text(self):
        """Get human-readable status text"""
        if self.status == 'paid':
            return 'Оплачено'
        elif self.status == 'partial':
            return 'Частично оплачено'
        elif self.is_overdue():
            return 'Просрочено'
        elif self.status == 'cancelled':
            return 'Отменено'
        else:
            return 'Ожидает оплаты'
    
    def days_until_due(self):
        """Get days until payment is due (negative if overdue)"""
        delta = self.due_date - date.today()
        return delta.days