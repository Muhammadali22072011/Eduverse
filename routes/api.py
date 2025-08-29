from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from models import db, User, School, Subject, ClassGroup, Grade, Payment, ScheduleEvent
from datetime import datetime
from models.role import Role

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/search/users')
@login_required
def search_users():
    """Search users API endpoint"""
    query = request.args.get('q', '')
    school_id = request.args.get('school_id', type=int)
    
    if not query or len(query) < 2:
        return jsonify({'users': []})
    
    # Build query
    user_query = User.query.filter(
        User.is_active == True,
        (User.first_name.ilike(f'%{query}%') |
         User.last_name.ilike(f'%{query}%') |
         User.username.ilike(f'%{query}%'))
    )
    
    # Filter by school if specified
    if school_id:
        from models.role import UserRole
        user_query = user_query.join(UserRole).filter(UserRole.school_id == school_id)
    
    users = user_query.limit(10).all()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email
        })
    
    return jsonify({'users': user_list})

@api_bp.route('/schools/<int:school_id>/subjects')
@login_required
def get_school_subjects(school_id):
    """Get subjects for a school"""
    # Check if user has access to school
    from routes.school import has_school_access
    school = School.query.get_or_404(school_id)
    
    if not has_school_access(current_user, school):
        abort(403)
    
    subjects = Subject.query.filter_by(
        school_id=school_id,
        is_active=True
    ).all()
    
    subject_list = []
    for subject in subjects:
        subject_list.append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.code,
            'color': subject.color
        })
    
    return jsonify({'subjects': subject_list})

@api_bp.route('/schools/<int:school_id>/classes')
@login_required
def get_school_classes(school_id):
    """Get classes for a school"""
    # Check if user has access to school
    from routes.school import has_school_access
    school = School.query.get_or_404(school_id)
    
    if not has_school_access(current_user, school):
        abort(403)
    
    classes = ClassGroup.query.filter_by(
        school_id=school_id,
        is_active=True
    ).all()
    
    class_list = []
    for class_group in classes:
        class_list.append({
            'id': class_group.id,
            'name': class_group.name,
            'description': class_group.description,
            'student_count': class_group.get_student_count()
        })
    
    return jsonify({'classes': class_list})

@api_bp.route('/grades/add', methods=['POST'])
@login_required
def add_grade():
    """Add new grade"""
    # Check if user is teacher
    if not current_user.has_role('teacher'):
        abort(403)
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['student_id', 'subject_id', 'grade', 'grade_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate grade value (1-10 scale)
    grade_value = int(data['grade'])
    if grade_value < 1 or grade_value > 10:
        return jsonify({'error': 'Grade must be between 1 and 10'}), 400
    
    # Check if user can grade this student/subject
    from models.role import UserRole
    teacher_role = UserRole.query.filter_by(
        user_id=current_user.id,
        role_id=Role.query.filter_by(name='teacher').first().id
    ).first()
    
    if not teacher_role:
        return jsonify({'error': 'Teacher role not found'}), 403
    
    # Create grade
    grade = Grade(
        grade=grade_value,
        comment=data.get('comment', ''),
        grade_type=data['grade_type'],
        subject_id=data['subject_id'],
        student_id=data['student_id'],
        teacher_id=current_user.id,
        date_given=datetime.now().date()
    )
    
    db.session.add(grade)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'grade_id': grade.id,
        'message': 'Grade added successfully'
    })

@api_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@login_required
def update_grade(grade_id):
    """Update existing grade"""
    grade = Grade.query.get_or_404(grade_id)
    
    # Check if user can edit this grade
    if not (current_user.id == grade.teacher_id or 
            current_user.has_role('school_admin') or 
            current_user.has_role('super_admin')):
        abort(403)
    
    data = request.get_json()
    
    # Update fields
    if 'grade' in data:
        grade_value = int(data['grade'])
        if grade_value < 1 or grade_value > 10:
            return jsonify({'error': 'Grade must be between 1 and 10'}), 400
        grade.grade = grade_value
    
    if 'comment' in data:
        grade.comment = data['comment']
    
    if 'grade_type' in data:
        grade.grade_type = data['grade_type']
    
    grade.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Grade updated successfully'
    })

@api_bp.route('/grades/<int:grade_id>', methods=['DELETE'])
@login_required
def delete_grade(grade_id):
    """Delete grade"""
    grade = Grade.query.get_or_404(grade_id)
    
    # Check if user can delete this grade
    if not (current_user.id == grade.teacher_id or 
            current_user.has_role('school_admin') or 
            current_user.has_role('super_admin')):
        abort(403)
    
    db.session.delete(grade)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Grade deleted successfully'
    })

@api_bp.route('/schedule/<int:school_id>')
@login_required
def get_school_schedule(school_id):
    """Get school schedule"""
    # Check if user has access to school
    from routes.school import has_school_access
    school = School.query.get_or_404(school_id)
    
    if not has_school_access(current_user, school):
        abort(403)
    
    # Get schedule events
    events = ScheduleEvent.query.filter_by(
        school_id=school_id,
        is_active=True
    ).all()
    
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'day_of_week': event.day_of_week,
            'start_time': event.start_time.strftime('%H:%M'),
            'end_time': event.end_time.strftime('%H:%M'),
            'event_type': event.event_type,
            'subject_id': event.subject_id,
            'class_group_id': event.class_group_id,
            'teacher_id': event.teacher_id,
            'room': event.room,
            'color': event.color
        })
    
    return jsonify({'events': event_list})

@api_bp.route('/payments/<int:school_id>')
@login_required
def get_school_payments(school_id):
    """Get school payments"""
    # Check if user has access to school
    from routes.school import has_school_access
    school = School.query.get_or_404(school_id)
    
    if not has_school_access(current_user, school):
        abort(403)
    
    # Get payments based on user role
    if current_user.has_role('student'):
        payments = Payment.query.filter_by(
            student_id=current_user.id,
            school_id=school_id
        ).all()
    else:
        payments = Payment.query.filter_by(school_id=school_id).all()
    
    payment_list = []
    for payment in payments:
        payment_list.append({
            'id': payment.id,
            'amount': float(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'due_date': payment.due_date.isoformat(),
            'paid_date': payment.paid_date.isoformat() if payment.paid_date else None,
            'student_name': payment.student.get_full_name(),
            'payment_type': payment.payment_type,
            'description': payment.description
        })
    
    return jsonify({'payments': payment_list})

@api_bp.route('/notifications')
@login_required
def get_notifications():
    """Get user notifications"""
    from models.notification import Notification
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    notification_list = []
    for notification in notifications.items:
        notification_list.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'is_important': notification.is_important,
            'requires_action': notification.requires_action,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'action_text': notification.action_text
        })
    
    return jsonify({
        'notifications': notification_list,
        'has_next': notifications.has_next,
        'has_prev': notifications.has_prev,
        'page': page,
        'pages': notifications.pages
    })

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Check if notification belongs to user
    if notification.user_id != current_user.id:
        abort(403)
    
    notification.mark_as_read()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Notification marked as read'
    })

@api_bp.route('/dashboard/stats')
@login_required
def get_dashboard_stats():
    """Get dashboard statistics for current user"""
    stats = {}
    
    # Get user's primary role
    primary_role = current_user.get_primary_role()
    
    if primary_role and primary_role.role.name == 'student':
        # Student stats
        from models.grade import Grade
        from models.payment import Payment
        
        stats['recent_grades'] = Grade.query.filter_by(
            student_id=current_user.id
        ).order_by(Grade.created_at.desc()).limit(5).count()
        
        stats['overdue_payments'] = Payment.query.filter_by(
            student_id=current_user.id,
            status='overdue'
        ).count()
        
    elif primary_role and primary_role.role.name == 'teacher':
        # Teacher stats
        from models.grade import Grade
        
        stats['grades_given'] = Grade.query.filter_by(
            teacher_id=current_user.id
        ).count()
        
        stats['recent_grades'] = Grade.query.filter_by(
            teacher_id=current_user.id
        ).order_by(Grade.created_at.desc()).limit(5).count()
    
    # Common stats
    from models.notification import Notification
    stats['unread_notifications'] = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify(stats)