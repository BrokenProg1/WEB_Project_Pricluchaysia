from flask_wtf import FlaskForm
import wtforms


class EditExc(FlaskForm):
    title = wtforms.StringField('Новое название')
    description = wtforms.StringField('Новое описание')
    price = wtforms.IntegerField('Новая цена')
    img = wtforms.FileField('Заставка экскурсии')
    submit = wtforms.SubmitField('Изменить')