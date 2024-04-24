from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

required_message = 'Пожалуйста, заполните это поле.'
length_message = 'Длина поля должна быть от %(min)d до %(max)d символов.'


class RegistrationForm(FlaskForm):
    # Поля
    login = StringField('Логин', validators=[
        DataRequired(message=required_message),
        Length(min=5, max=25, message=length_message % {'min': 5, 'max': 25})
    ])
    first_name = StringField('Фамилия', validators=[
        DataRequired(message=required_message),
        Length(min=5, max=25, message=length_message % {'min': 5, 'max': 25})
    ])
    middle_name = StringField('Имя', validators=[
        DataRequired(message=required_message),
        Length(min=5, max=20, message=length_message % {'min': 5, 'max': 20})
    ])
    last_name = StringField('Отчество', validators=[
        DataRequired(message=required_message),
        Length(min=5, max=20, message=length_message % {'min': 5, 'max': 20})
    ])
    password = PasswordField('Новый пароль', validators=[
        DataRequired(message=required_message),
        EqualTo('confirm', message='Пароли должны совпадать.'),
        Length(min=8, max=128, message=length_message % {'min': 8, 'max': 128}),
        Regexp(regex=r'^(?=.*[a-zа-я])(?=.*[A-ZА-Я])(?=.*\d)(?!.*\s)[a-zA-Zа-яА-Я0-9~!@#$%^&*()_\-+{}\[\]|\\":;\'<>?,.\/]*$',
               message='Пароль должен содержать не менее 8 символов, включая как минимум одну заглавную и одну строчную букву, одну цифру, без пробелов и только арабские цифры и буквы. Разрешены следующие символы: ~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } < > / \ | " \' . , :')
    ])
    confirm = PasswordField('Повторите пароль', validators=[
        DataRequired(message=required_message)
    ])
    select_role = SelectField('Роль', coerce=int, validators=[
        DataRequired(message=required_message)
    ], choices=[
        (1, 'Администратор'),
        (2, 'Пользователь'),
        (3, 'Другая роль')
    ])
    submit = SubmitField('Сохранить')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Введите старый пароль', validators=[
        DataRequired(message=required_message)
    ])
    password = PasswordField('Введите Новый пароль', validators=[
        DataRequired(message=required_message),
        EqualTo('confirm', message='Пароли должны совпадать.'),
        Length(min=8, max=128, message=length_message % {'min': 8, 'max': 128}),
        Regexp(
            regex=r'^(?=.*[a-zа-я])(?=.*[A-ZА-Я])(?=.*\d)(?!.*\s)[a-zA-Zа-яА-Я0-9~!@#$%^&*()_\-+{}\[\]|\\":;\'<>?,.\/]*$',
            message='Пароль должен содержать не менее 8 символов, включая как минимум одну заглавную и одну строчную букву, одну цифру, без пробелов и только арабские цифры и буквы. Разрешены следующие символы: ~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } < > / \ | " \' . , :')
    ])
    confirm = PasswordField('Повторите новый пароль', validators=[
        DataRequired(message=required_message)
    ])
    submit = SubmitField('Сохранить')