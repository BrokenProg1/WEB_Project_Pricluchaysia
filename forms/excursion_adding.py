from flask_wtf import FlaskForm
import wtforms


class AddiExc(FlaskForm):
    # Форма для создания экскурсий
    title = wtforms.StringField('Название')
    description = wtforms.StringField('Описание')
    price = wtforms.IntegerField('Цена')
    img = wtforms.FileField('Заставка экскурсии')
    way = wtforms.TextAreaField('Точки маршрута экскурсии (указывать адреса в " через ,)')
    submit = wtforms.SubmitField('Создать')