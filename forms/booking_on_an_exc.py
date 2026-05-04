from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired


class BookOnAnExc(FlaskForm):
    count_of_people = wtforms.IntegerField('Количество желающих записаться', default=1, validators=[DataRequired()])
    submit = wtforms.SubmitField('Записаться')