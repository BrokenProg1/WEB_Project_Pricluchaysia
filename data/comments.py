import sqlalchemy
import datetime

from data.db_session import DeclaratingDataBase


class Comment(DeclaratingDataBase):
    # Шаблон объекта отзыва на экскурсию
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_event = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('excursions.id'))
    id_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name_user = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('users.login'))
    role_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.role'))
    text = sqlalchemy.Column(sqlalchemy.Text)
    date = sqlalchemy.Column(sqlalchemy.String, default=datetime.datetime.now)


    def __repr__(self):
        return f"""<Comment> Id: {self.id} Id of author: {self.id_user} Id of commenting excursion: {self.id_event}
        Date of writing: {self.date}"""