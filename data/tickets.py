import sqlalchemy

from data.db_session import DeclaratingDataBase


class Ticket(DeclaratingDataBase):
    __tablename__ = 'tickets'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_event = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('excursions.id'))
    name_event = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('excursions.title'))
    price_event = sqlalchemy.Column(sqlalchemy.Float, sqlalchemy.ForeignKey('excursions.price'))
    id_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.login'))
    count_of_people = sqlalchemy.Column(sqlalchemy.Integer, default=1)


    def __repr__(self):
        return f"""<User> Id: {self.id} Id of excursion: {self.id_event} Id of customer: {self.id_user}
        Title of excursion: {self.name_event} Price per person: {self.price_event}
        Count of people: {self.count_of_people}"""