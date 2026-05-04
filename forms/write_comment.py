from flask_wtf import FlaskForm
import wtforms


class WriteComment(FlaskForm):
    comment = wtforms.StringField('Напишите отзыв об экскурсии...', default='...')
    submit = wtforms.SubmitField('Отправить')