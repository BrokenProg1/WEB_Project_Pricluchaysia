from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    # Форма для авторизации
    username_field = StringField('Имя / Логин / Ник', validators=[DataRequired()])
    email_field = StringField('Электронная почта', validators=[DataRequired(), Email()])
    password_field = PasswordField('Пароль', validators=[DataRequired()])
    submit_button = SubmitField('Войти')