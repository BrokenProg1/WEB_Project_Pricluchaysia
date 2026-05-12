from flask_wtf import FlaskForm
import wtforms


class WriteComment(FlaskForm):
    # Форма для написания отзыва под экскурсией
    comment = wtforms.TextAreaField(render_kw={'placeholder': 'Напишите отзыв об экскурсии...'})
    submit = wtforms.SubmitField('Отправить отзыв об экскурсии')