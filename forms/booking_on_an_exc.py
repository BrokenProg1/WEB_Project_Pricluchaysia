from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired


class BookOnAnExc(FlaskForm):
    # Форма для записи на экскурсию
    count_of_people = wtforms.IntegerField('Количество желающих записаться', default=1, validators=[DataRequired()])
    submit = wtforms.SubmitField('Записаться')