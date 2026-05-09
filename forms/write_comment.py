from flask_wtf import FlaskForm
import wtforms


class WriteComment(FlaskForm):
    comment = wtforms.TextAreaField(render_kw={'placeholder': 'Напишите отзыв об экскурсии...'})
    submit = wtforms.SubmitField('Отправить отзыв об экскурсии')