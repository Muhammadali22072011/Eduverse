from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, School, SchoolSettings, User, Role, UserRole, Subject, ClassGroup
from forms.school_forms import SchoolCreationForm, SchoolSettingsForm
import re
import uuid

school_bp = Blueprint('school', __name__)

@school_bp.route('/schools')
def schools_list():
    """List all public schools"""
    page = request.args.get('page', 1, type=int)
    schools = School.query.filter_by(is_active=True).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('school/schools_list.html', schools=schools, title='Школы')

@school_bp.route('/school/<slug>')
def school_view(slug):
    """View school details"""
    school = School.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Get school statistics
    student_count = UserRole.query.join(Role).filter(
        Role.name == 'student',
        UserRole.school_id == school.id,
        UserRole.is_active == True
    ).count()
    
    teacher_count = UserRole.query.join(Role).filter(
        Role.name == 'teacher',
        UserRole.school_id == school.id,
        UserRole.is_active == True
    ).count()
    
    # Get school subjects
    subjects = Subject.query.filter_by(school_id=school.id, is_active=True).all()
    
    # Get school classes
    classes = ClassGroup.query.filter_by(school_id=school.id, is_active=True).all()
    
    context = {
        'school': school,
        'student_count': student_count,
        'teacher_count': teacher_count,
        'subjects': subjects,
        'classes': classes
    }
    
    return render_template('school/school_view.html', **context, title=school.name)

@school_bp.route('/school/create', methods=['GET', 'POST'])
@login_required
def school_create():
    """Create new school"""
    # Check if user can create schools
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        flash('У вас нет прав для создания школ.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = SchoolCreationForm()
    if form.validate_on_submit():
        # Generate slug from name
        slug = re.sub(r'[^\w\s-]', '', form.name.data.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Check if slug is unique
        if School.query.filter_by(slug=slug).first():
            slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        
        # Create school
        school = School(
            name=form.name.data,
            slug=slug,
            description=form.description.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            website=form.website.data,
            owner_id=current_user.id
        )
        
        db.session.add(school)
        db.session.flush()  # Get the school ID
        
        # Create school settings
        settings = SchoolSettings(school_id=school.id)
        db.session.add(settings)
        
        # Assign school admin role to creator
        school_admin_role = Role.query.filter_by(name='school_admin').first()
        if school_admin_role:
            user_role = UserRole(
                user_id=current_user.id,
                role_id=school_admin_role.id,
                school_id=school.id,
                assigned_by=current_user.id
            )
            db.session.add(user_role)
        
        db.session.commit()
        
        flash(f'Школа "{school.name}" успешно создана!', 'success')
        return redirect(url_for('school.school_view', slug=school.slug))
    
    return render_template('school/school_create.html', form=form, title='Создание школы')

@school_bp.route('/school/<slug>/admin')
@login_required
def school_admin(slug):
    """School administration panel"""
    school = School.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Check if user has admin access to this school
    if not has_school_access(current_user, school, ['school_admin', 'super_admin', 'project_admin']):
        abort(403)
    
    # Get school statistics
    stats = get_school_statistics(school)
    
    return render_template('school/school_admin.html', 
                         school=school, 
                         stats=stats,
                         title=f'Администрирование - {school.name}')

@school_bp.route('/school/<slug>/settings', methods=['GET', 'POST'])
@login_required
def school_settings(slug):
    """School settings page"""
    school = School.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Check if user has admin access to this school
    if not has_school_access(current_user, school, ['school_admin', 'super_admin', 'project_admin']):
        abort(403)
    
    form = SchoolSettingsForm(obj=school.settings)
    
    if form.validate_on_submit():
        # Update school settings
        for field in form:
            if field.name != 'csrf_token' and hasattr(school.settings, field.name):
                setattr(school.settings, field.name, field.data)
        
        db.session.commit()
        flash('Настройки школы обновлены!', 'success')
        return redirect(url_for('school.school_settings', slug=slug))
    
    return render_template('school/school_settings.html', 
                         form=form, 
                         school=school,
                         title=f'Настройки - {school.name}')

@school_bp.route('/school/<slug>/users')
@login_required
def school_users(slug):
    """School users management"""
    school = School.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Check if user has admin access to this school
    if not has_school_access(current_user, school, ['school_admin', 'super_admin', 'project_admin']):
        abort(403)
    
    # Get users by role
    users_by_role = {}
    roles = Role.query.all()
    
    for role in roles:
        user_roles = UserRole.query.filter_by(
            role_id=role.id,
            school_id=school.id,
            is_active=True
        ).all()
        users_by_role[role.name] = [ur.user for ur in user_roles]
    
    return render_template('school/school_users.html', 
                         school=school, 
                         users_by_role=users_by_role,
                         title=f'Пользователи - {school.name}')

@school_bp.route('/school/<slug>/schedule')
@login_required
def school_schedule(slug):
    """School schedule view"""
    school = School.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Check if user has access to this school
    if not has_school_access(current_user, school):
        abort(403)
    
    # Get schedule data
    from models.schedule import Schedule, ScheduleEvent
    schedules = Schedule.query.filter_by(school_id=school.id, is_active=True).all()
    
    return render_template('school/school_schedule.html', 
                         school=school, 
                         schedules=schedules,
                         title=f'Расписание - {school.name}')

@school_bp.route('/school/<slug>/grades')
@login_required
def school_grades(slug):
    """School grades view"""
    school = School.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Check if user has access to this school
    if not has_school_access(current_user, school):
        abort(403)
    
    # Get grades data based on user role
    from models.grade import Grade
    if current_user.has_role('student'):
        grades = Grade.query.filter_by(
            student_id=current_user.id
        ).join(Subject).filter(Subject.school_id == school.id).all()
    elif current_user.has_role('teacher'):
        grades = Grade.query.filter_by(
            teacher_id=current_user.id
        ).join(Subject).filter(Subject.school_id == school.id).all()
    else:
        grades = Grade.query.join(Subject).filter(Subject.school_id == school.id).all()
    
    return render_template('school/school_grades.html', 
                         school=school, 
                         grades=grades,
                         title=f'Оценки - {school.name}')

@school_bp.route('/school/<slug>/payments')
@login_required
def school_payments(slug):
    """School payments view"""
    school = School.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Check if user has access to this school
    if not has_school_access(current_user, school):
        abort(403)
    
    # Get payments data based on user role
    from models.payment import Payment
    if current_user.has_role('student'):
        payments = Payment.query.filter_by(
            student_id=current_user.id,
            school_id=school.id
        ).all()
    else:
        payments = Payment.query.filter_by(school_id=school.id).all()
    
    return render_template('school/school_payments.html', 
                         school=school, 
                         payments=payments,
                         title=f'Оплаты - {school.name}')

def has_school_access(user, school, required_roles=None):
    """Check if user has access to school"""
    if not user.is_authenticated:
        return False
    
    # Super admin has access to everything
    if user.has_role('super_admin'):
        return True
    
    # Project admin has access to everything
    if user.has_role('project_admin'):
        return True
    
    # Check if user has role in this school
    user_roles = UserRole.query.filter_by(
        user_id=user.id,
        school_id=school.id,
        is_active=True
    ).all()
    
    if not user_roles:
        return False
    
    if required_roles:
        user_role_names = [ur.role.name for ur in user_roles]
        return any(role in user_role_names for role in required_roles)
    
    return True

def get_school_statistics(school):
    """Get comprehensive school statistics"""
    stats = {}
    
    # User counts
    stats['total_students'] = UserRole.query.join(Role).filter(
        Role.name == 'student',
        UserRole.school_id == school.id,
        UserRole.is_active == True
    ).count()
    
    stats['total_teachers'] = UserRole.query.join(Role).filter(
        Role.name == 'teacher',
        UserRole.school_id == school.id,
        UserRole.is_active == True
    ).count()
    
    stats['total_admins'] = UserRole.query.join(Role).filter(
        Role.name == 'school_admin',
        UserRole.school_id == school.id,
        UserRole.is_active == True
    ).count()
    
    # Academic counts
    stats['total_subjects'] = Subject.query.filter_by(
        school_id=school.id, 
        is_active=True
    ).count()
    
    stats['total_classes'] = ClassGroup.query.filter_by(
        school_id=school.id, 
        is_active=True
    ).count()
    
    # Payment statistics
    from models.payment import Payment
    stats['total_payments'] = Payment.query.filter_by(school_id=school.id).count()
    stats['overdue_payments'] = Payment.query.filter_by(
        school_id=school.id, 
        status='overdue'
    ).count()
    
    return stats