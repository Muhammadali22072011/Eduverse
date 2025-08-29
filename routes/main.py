from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import School, User, Role, UserRole

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Get some public schools for display
    schools = School.query.filter_by(is_active=True, is_verified=True).limit(6).all()
    
    return render_template('main/index.html', schools=schools, title='EduVerse - Образовательная платформа')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's schools
    user_schools = current_user.get_schools()
    
    # Get user's primary role
    primary_role = current_user.get_primary_role()
    
    # Get recent notifications
    from models.notification import Notification
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get recent chat messages
    from models.chat import ChatParticipant, ChatMessage
    chat_participants = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    recent_messages = []
    for participant in chat_participants:
        messages = ChatMessage.query.filter_by(
            chat_id=participant.chat_id
        ).order_by(ChatMessage.created_at.desc()).limit(3).all()
        recent_messages.extend(messages)
    
    # Sort by creation time and get latest 10
    recent_messages.sort(key=lambda x: x.created_at, reverse=True)
    recent_messages = recent_messages[:10]
    
    context = {
        'user_schools': user_schools,
        'primary_role': primary_role,
        'notifications': notifications,
        'recent_messages': recent_messages
    }
    
    # Role-specific dashboard data
    if primary_role and primary_role.role.name == 'student':
        context.update(get_student_dashboard_data())
    elif primary_role and primary_role.role.name == 'teacher':
        context.update(get_teacher_dashboard_data())
    elif primary_role and primary_role.role.name == 'school_admin':
        context.update(get_school_admin_dashboard_data())
    elif primary_role and primary_role.role.name == 'super_admin':
        context.update(get_super_admin_dashboard_data())
    
    return render_template('main/dashboard.html', **context, title='Панель управления')

def get_student_dashboard_data():
    """Get student-specific dashboard data"""
    from models.grade import Grade
    from models.payment import Payment
    from models.schedule import ScheduleEvent
    
    # Get recent grades
    recent_grades = Grade.query.filter_by(
        student_id=current_user.id
    ).order_by(Grade.created_at.desc()).limit(5).all()
    
    # Get payment status
    payments = Payment.query.filter_by(
        student_id=current_user.id
    ).order_by(Payment.due_date.desc()).limit(5).all()
    
    # Get today's schedule
    from datetime import datetime, date
    today = date.today()
    today_schedule = ScheduleEvent.query.filter(
        ScheduleEvent.day_of_week == today.weekday(),
        ScheduleEvent.is_active == True
    ).all()
    
    return {
        'recent_grades': recent_grades,
        'payments': payments,
        'today_schedule': today_schedule
    }

def get_teacher_dashboard_data():
    """Get teacher-specific dashboard data"""
    from models.grade import Grade
    from models.schedule import ScheduleEvent
    
    # Get recent grades given by teacher
    recent_grades = Grade.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Grade.created_at.desc()).limit(5).all()
    
    # Get today's lessons
    from datetime import date
    today = date.today()
    today_lessons = ScheduleEvent.query.filter(
        ScheduleEvent.teacher_id == current_user.id,
        ScheduleEvent.day_of_week == today.weekday(),
        ScheduleEvent.is_active == True
    ).all()
    
    return {
        'recent_grades': recent_grades,
        'today_lessons': today_lessons
    }

def get_school_admin_dashboard_data():
    """Get school admin-specific dashboard data"""
    from models.grade import Grade
    from models.payment import Payment
    from models.user import User
    
    # Get school statistics
    school_stats = {}
    for school in current_user.get_schools():
        if school:
            # Count students
            student_count = UserRole.query.join(Role).filter(
                Role.name == 'student',
                UserRole.school_id == school.id,
                UserRole.is_active == True
            ).count()
            
            # Count teachers
            teacher_count = UserRole.query.join(Role).filter(
                Role.name == 'teacher',
                UserRole.school_id == school.id,
                UserRole.is_active == True
            ).count()
            
            # Count overdue payments
            overdue_payments = Payment.query.filter_by(
                school_id=school.id,
                status='overdue'
            ).count()
            
            school_stats[school.id] = {
                'name': school.name,
                'student_count': student_count,
                'teacher_count': teacher_count,
                'overdue_payments': overdue_payments
            }
    
    return {
        'school_stats': school_stats
    }

def get_super_admin_dashboard_data():
    """Get super admin-specific dashboard data"""
    # Get platform statistics
    total_schools = School.query.count()
    total_users = User.query.count()
    verified_schools = School.query.filter_by(is_verified=True).count()
    active_schools = School.query.filter_by(is_active=True).count()
    
    # Get recent schools
    recent_schools = School.query.order_by(School.created_at.desc()).limit(5).all()
    
    return {
        'total_schools': total_schools,
        'total_users': total_users,
        'verified_schools': verified_schools,
        'active_schools': active_schools,
        'recent_schools': recent_schools
    }

@main_bp.route('/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))
    
    # Search in schools
    schools = School.query.filter(
        School.name.ilike(f'%{query}%') |
        School.description.ilike(f'%{query}%')
    ).filter_by(is_active=True).limit(10).all()
    
    # Search in users (public info only)
    users = User.query.filter(
        User.first_name.ilike(f'%{query}%') |
        User.last_name.ilike(f'%{query}%') |
        User.username.ilike(f'%{query}%')
    ).filter_by(is_active=True).limit(10).all()
    
    return render_template('main/search.html', 
                         query=query, 
                         schools=schools, 
                         users=users,
                         title=f'Поиск: {query}')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html', title='О платформе')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html', title='Контакты')