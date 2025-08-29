from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, URL, Optional

class SchoolCreationForm(FlaskForm):
    """School creation form"""
    name = StringField('Название школы', validators=[
        DataRequired(message='Название школы обязательно'),
        Length(min=3, max=200, message='Название должно содержать от 3 до 200 символов')
    ])
    
    description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=1000, message='Описание не должно превышать 1000 символов')
    ])
    
    address = TextAreaField('Адрес', validators=[
        Optional(),
        Length(max=500, message='Адрес не должен превышать 500 символов')
    ])
    
    phone = StringField('Телефон', validators=[
        Optional(),
        Length(max=20, message='Телефон не должен превышать 20 символов')
    ])
    
    email = StringField('Email', validators=[
        Optional(),
        Email(message='Введите корректный email адрес'),
        Length(max=120, message='Email не должен превышать 120 символов')
    ])
    
    website = StringField('Веб-сайт', validators=[
        Optional(),
        URL(message='Введите корректный URL'),
        Length(max=200, message='URL не должен превышать 200 символов')
    ])
    
    submit = SubmitField('Создать школу')

class SchoolSettingsForm(FlaskForm):
    """School settings form"""
    # General settings
    timezone = SelectField('Часовой пояс', choices=[
        ('UTC', 'UTC'),
        ('Europe/Moscow', 'Москва (UTC+3)'),
        ('Europe/Kaliningrad', 'Калининград (UTC+2)'),
        ('Asia/Yekaterinburg', 'Екатеринбург (UTC+5)'),
        ('Asia/Novosibirsk', 'Новосибирск (UTC+6)'),
        ('Asia/Krasnoyarsk', 'Красноярск (UTC+7)'),
        ('Asia/Irkutsk', 'Иркутск (UTC+8)'),
        ('Asia/Yakutsk', 'Якутск (UTC+9)'),
        ('Asia/Vladivostok', 'Владивосток (UTC+10)'),
        ('Asia/Magadan', 'Магадан (UTC+11)'),
        ('Asia/Kamchatka', 'Камчатка (UTC+12)')
    ])
    
    language = SelectField('Язык', choices=[
        ('ru', 'Русский'),
        ('en', 'English'),
        ('kz', 'Қазақша'),
        ('be', 'Беларуская'),
        ('uk', 'Українська')
    ])
    
    currency = SelectField('Валюта', choices=[
        ('RUB', 'Российский рубль (₽)'),
        ('USD', 'Доллар США ($)'),
        ('EUR', 'Евро (€)'),
        ('KZT', 'Казахстанский тенге (₸)'),
        ('BYN', 'Белорусский рубль (Br)'),
        ('UAH', 'Украинская гривна (₴)')
    ])
    
    # Academic settings
    grading_system = SelectField('Система оценок', choices=[
        ('10-point', '10-балльная система'),
        ('5-point', '5-балльная система'),
        ('100-point', '100-балльная система'),
        ('letter', 'Буквенная система (A-F)')
    ])
    
    assignment_mode = SelectField('Режим прикрепления учеников', choices=[
        ('by_class', 'По классам'),
        ('by_subject', 'По предметам'),
        ('mixed', 'Смешанный режим')
    ])
    
    # Payment settings
    payment_due_day = SelectField('День оплаты', choices=[
        (str(i), str(i)) for i in range(1, 29)
    ])
    
    payment_reminder_days = SelectField('Дней до напоминания', choices=[
        (str(i), str(i)) for i in range(1, 31)
    ])
    
    # Chat settings
    chat_enabled = SelectField('Включить чаты', choices=[
        ('true', 'Да'),
        ('false', 'Нет')
    ])
    
    chat_moderation = SelectField('Модерация чатов', choices=[
        ('true', 'Да'),
        ('false', 'Нет')
    ])
    
    # Notification settings
    email_notifications = SelectField('Email уведомления', choices=[
        ('true', 'Да'),
        ('false', 'Нет')
    ])
    
    sms_notifications = SelectField('SMS уведомления', choices=[
        ('true', 'Да'),
        ('false', 'Нет')
    ])
    
    push_notifications = SelectField('Push уведомления', choices=[
        ('true', 'Да'),
        ('false', 'Нет')
    ])
    
    submit = SubmitField('Сохранить настройки')