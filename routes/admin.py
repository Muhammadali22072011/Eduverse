from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User, Role, UserRole, School, SchoolSettings

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    # Get platform statistics
    stats = get_platform_statistics()
    
    # Get recent activities
    recent_schools = School.query.order_by(School.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_schools=recent_schools,
                         recent_users=recent_users,
                         title='Администрирование платформы')

@admin_bp.route('/users')
@login_required
def users_management():
    """Users management"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users_management.html', 
                         users=users,
                         title='Управление пользователями')

@admin_bp.route('/schools')
@login_required
def schools_management():
    """Schools management"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    schools = School.query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/schools_management.html', 
                         schools=schools,
                         title='Управление школами')

@admin_bp.route('/roles')
@login_required
def roles_management():
    """Roles management"""
    if not current_user.has_role('super_admin'):
        abort(403)
    
    roles = Role.query.all()
    
    return render_template('admin/roles_management.html', 
                         roles=roles,
                         title='Управление ролями')

@admin_bp.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    """User detail view"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    
    return render_template('admin/user_detail.html', 
                         user=user,
                         user_roles=user_roles,
                         title=f'Пользователь: {user.username}')

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    """Edit user"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Update user data
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Пользователь обновлен!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('admin/user_edit.html', 
                         user=user,
                         title=f'Редактирование: {user.username}')

@admin_bp.route('/user/<int:user_id>/roles', methods=['GET', 'POST'])
@login_required
def user_roles(user_id):
    """Manage user roles"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Handle role assignment/removal
        action = request.form.get('action')
        role_id = request.form.get('role_id')
        school_id = request.form.get('school_id')
        
        if action == 'add_role':
            # Add new role
            user_role = UserRole(
                user_id=user.id,
                role_id=role_id,
                school_id=school_id if school_id else None,
                assigned_by=current_user.id
            )
            db.session.add(user_role)
            flash('Роль назначена!', 'success')
        
        elif action == 'remove_role':
            # Remove role
            user_role = UserRole.query.filter_by(
                user_id=user.id,
                role_id=role_id,
                school_id=school_id if school_id else None
            ).first()
            if user_role:
                db.session.delete(user_role)
                flash('Роль удалена!', 'success')
        
        db.session.commit()
        return redirect(url_for('admin.user_roles', user_id=user.id))
    
    # Get all roles and schools
    roles = Role.query.all()
    schools = School.query.filter_by(is_active=True).all()
    user_roles = UserRole.query.filter_by(user_id=user.id).all()
    
    return render_template('admin/user_roles.html', 
                         user=user,
                         roles=roles,
                         schools=schools,
                         user_roles=user_roles,
                         title=f'Роли пользователя: {user.username}')

@admin_bp.route('/school/<int:school_id>')
@login_required
def school_detail(school_id):
    """School detail view"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    school = School.query.get_or_404(school_id)
    
    # Get school statistics
    stats = get_school_statistics(school)
    
    return render_template('admin/school_detail.html', 
                         school=school,
                         stats=stats,
                         title=f'Школа: {school.name}')

@admin_bp.route('/school/<int:school_id>/verify', methods=['POST'])
@login_required
def verify_school(school_id):
    """Verify school"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    school = School.query.get_or_404(school_id)
    school.is_verified = True
    db.session.commit()
    
    flash(f'Школа "{school.name}" верифицирована!', 'success')
    return redirect(url_for('admin.school_detail', school_id=school.id))

@admin_bp.route('/school/<int:school_id>/activate', methods=['POST'])
@login_required
def activate_school(school_id):
    """Activate/deactivate school"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    school = School.query.get_or_404(school_id)
    action = request.form.get('action')
    
    if action == 'activate':
        school.is_active = True
        flash(f'Школа "{school.name}" активирована!', 'success')
    elif action == 'deactivate':
        school.is_active = False
        flash(f'Школа "{school.name}" деактивирована!', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.school_detail', school_id=school.id))

@admin_bp.route('/statistics')
@login_required
def platform_statistics():
    """Platform statistics"""
    if not (current_user.has_role('super_admin') or current_user.has_role('project_admin')):
        abort(403)
    
    stats = get_platform_statistics()
    
    # Get monthly user growth
    from datetime import datetime, timedelta
    monthly_stats = []
    for i in range(12):
        date = datetime.now() - timedelta(days=30*i)
        month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = month_start + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        user_count = User.query.filter(
            User.created_at >= month_start,
            User.created_at <= month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'users': user_count
        })
    
    monthly_stats.reverse()
    
    return render_template('admin/statistics.html', 
                         stats=stats,
                         monthly_stats=monthly_stats,
                         title='Статистика платформы')

def get_platform_statistics():
    """Get comprehensive platform statistics"""
    stats = {}
    
    # User statistics
    stats['total_users'] = User.query.count()
    stats['active_users'] = User.query.filter_by(is_active=True).count()
    stats['verified_users'] = User.query.filter_by(is_verified=True).count()
    
    # School statistics
    stats['total_schools'] = School.query.count()
    stats['active_schools'] = School.query.filter_by(is_active=True).count()
    stats['verified_schools'] = School.query.filter_by(is_verified=True).count()
    
    # Role statistics
    roles = Role.query.all()
    for role in roles:
        count = UserRole.query.filter_by(role_id=role.id, is_active=True).count()
        stats[f'{role.name}_count'] = count
    
    return stats

def get_school_statistics(school):
    """Get school statistics for admin view"""
    stats = {}
    
    # User counts by role
    roles = Role.query.all()
    for role in roles:
        count = UserRole.query.filter_by(
            role_id=role.id,
            school_id=school.id,
            is_active=True
        ).count()
        stats[f'{role.name}_count'] = count
    
    # Academic counts
    from models.subject import Subject
    from models.class_group import ClassGroup
    stats['subjects_count'] = Subject.query.filter_by(
        school_id=school.id, 
        is_active=True
    ).count()
    
    stats['classes_count'] = ClassGroup.query.filter_by(
        school_id=school.id, 
        is_active=True
    ).count()
    
    return stats