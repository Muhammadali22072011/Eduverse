from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional

class ChatCreationForm(FlaskForm):
    """Chat creation form"""
    name = StringField('Название чата', validators=[
        Optional(),
        Length(max=200, message='Название не должно превышать 200 символов')
    ])
    
    chat_type = SelectField('Тип чата', choices=[
        ('private', 'Приватный'),
        ('group', 'Групповой'),
        ('subject', 'По предмету'),
        ('class', 'По классу'),
        ('administrative', 'Административный')
    ], validators=[
        DataRequired(message='Выберите тип чата')
    ])
    
    description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=500, message='Описание не должно превышать 500 символов')
    ])
    
    school_id = SelectField('Школа', coerce=int, validators=[
        Optional()
    ])
    
    subject_id = SelectField('Предмет', coerce=int, validators=[
        Optional()
    ])
    
    class_group_id = SelectField('Класс', coerce=int, validators=[
        Optional()
    ])
    
    participants = HiddenField('Участники')
    
    submit = SubmitField('Создать чат')

class MessageForm(FlaskForm):
    """Message form for chat"""
    message = TextAreaField('Сообщение', validators=[
        DataRequired(message='Введите текст сообщения'),
        Length(min=1, max=1000, message='Сообщение должно содержать от 1 до 1000 символов')
    ])
    
    submit = SubmitField('Отправить')