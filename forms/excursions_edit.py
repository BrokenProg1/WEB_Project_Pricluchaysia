from flask_wtf import FlaskForm
import wtforms


class EditExc(FlaskForm):
    title = wtforms.StringField('Новое название')
    description = wtforms.StringField('Новое описание')
    price = wtforms.IntegerField('Новая цена')
    img = wtforms.FileField('Заставка экскурсии')
    way = wtforms.TextAreaField('Точки маршрута экскурсии (указывать адреса в " через ,)')
    submit = wtforms.SubmitField('Изменить')