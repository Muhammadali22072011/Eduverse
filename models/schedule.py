from datetime import datetime, time, timedelta
from .user import db

class Schedule(db.Model):
    """Schedule model for school timetables"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    academic_year = db.Column(db.String(9))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    school = db.relationship('School', back_populates='schedules')
    events = db.relationship('ScheduleEvent', back_populates='schedule', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Schedule {self.name}>'

class ScheduleEvent(db.Model):
    """Individual schedule events/lessons"""
    __tablename__ = 'schedule_events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), default='lesson')  # lesson, exam, event, break
    
    # Time settings
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    # Date settings (for one-time events)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_recurring = db.Column(db.Boolean, default=True)
    
    # Academic settings
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room = db.Column(db.String(50))
    
    # Event settings
    color = db.Column(db.String(7), default='#007bff')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    
    # Relationships
    schedule = db.relationship('Schedule', back_populates='events')
    subject = db.relationship('Subject')
    class_group = db.relationship('ClassGroup')
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    
    def __repr__(self):
        return f'<ScheduleEvent {self.title}>'
    
    def get_duration_minutes(self):
        """Get event duration in minutes"""
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)
    
    def is_today(self, date=None):
        """Check if event occurs on given date"""
        if date is None:
            date = datetime.now().date()
        
        if not self.is_recurring:
            return self.start_date == date
        
        # For recurring events, check day of week
        return date.weekday() == self.day_of_week
    
    def get_next_occurrence(self, from_date=None):
        """Get next occurrence of this event"""
        if from_date is None:
            from_date = datetime.now().date()
        
        if not self.is_recurring:
            if self.start_date and self.start_date >= from_date:
                return self.start_date
            return None
        
        # Calculate next occurrence based on day of week
        days_ahead = self.day_of_week - from_date.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        next_date = from_date + timedelta(days=days_ahead)
        return next_date