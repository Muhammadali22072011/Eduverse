from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

from models import db, User, Role, UserRole
from forms.auth_forms import LoginForm, RegistrationForm, UserProfileForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.dashboard')
                
                flash(f'Добро пожаловать, {user.get_full_name()}!', 'success')
                return redirect(next_page)
            else:
                flash('Ваш аккаунт заблокирован. Обратитесь к администратору.', 'error')
        else:
            flash('Неверное имя пользователя или пароль.', 'error')
    
    return render_template('auth/login.html', form=form, title='Вход в систему')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Пользователь с таким именем уже существует.', 'error')
            return render_template('auth/register.html', form=form, title='Регистрация')
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Пользователь с таким email уже существует.', 'error')
            return render_template('auth/register.html', form=form, title='Регистрация')
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            phone=form.phone.data
        )
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Assign default role (student)
        student_role = Role.query.filter_by(name='student').first()
        if student_role:
            user_role = UserRole(
                user_id=user.id,
                role_id=student_role.id
            )
            db.session.add(user_role)
        
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Регистрация')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Вы успешно вышли из системы.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = UserProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Handle avatar upload
        if form.avatar.data:
            file = form.avatar.data
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                current_user.avatar = filename
        
        # Update user data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.middle_name = form.middle_name.data
        current_user.phone = form.phone.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash('Профиль успешно обновлен!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form, title='Мой профиль')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Текущий пароль неверен.', 'error')
        elif new_password != confirm_password:
            flash('Новые пароли не совпадают.', 'error')
        elif len(new_password) < 6:
            flash('Новый пароль должен содержать минимум 6 символов.', 'error')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', title='Смена пароля')

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS