from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=3, max=80, message='Имя пользователя должно содержать от 3 до 80 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=3, max=80, message='Имя пользователя должно содержать от 3 до 80 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email адрес')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтверждение пароля обязательно'),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    first_name = StringField('Имя', validators=[
        DataRequired(message='Имя обязательно'),
        Length(max=50, message='Имя не должно превышать 50 символов')
    ])
    last_name = StringField('Фамилия', validators=[
        DataRequired(message='Фамилия обязательна'),
        Length(max=50, message='Фамилия не должна превышать 50 символов')
    ])
    middle_name = StringField('Отчество', validators=[
        Length(max=50, message='Отчество не должно превышать 50 символов')
    ])
    phone = StringField('Телефон', validators=[
        Length(max=20, message='Телефон не должен превышать 20 символов')
    ])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Пользователь с таким именем уже существует.')
    
    def validate_email(self, email):
        """Check if email is already taken"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Пользователь с таким email уже существует.')

class UserProfileForm(FlaskForm):
    """User profile update form"""
    first_name = StringField('Имя', validators=[
        DataRequired(message='Имя обязательно'),
        Length(max=50, message='Имя не должно превышать 50 символов')
    ])
    last_name = StringField('Фамилия', validators=[
        DataRequired(message='Фамилия обязательна'),
        Length(max=50, message='Фамилия не должна превышать 50 символов')
    ])
    middle_name = StringField('Отчество', validators=[
        Length(max=50, message='Отчество не должно превышать 50 символов')
    ])
    phone = StringField('Телефон', validators=[
        Length(max=20, message='Телефон не должен превышать 20 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email адрес')
    ])
    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Разрешены только изображения!')
    ])
    submit = SubmitField('Сохранить изменения')
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if kwargs.get('obj'):
            self.original_email = kwargs['obj'].email
    
    def validate_email(self, email):
        """Check if email is already taken by another user"""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Пользователь с таким email уже существует.')