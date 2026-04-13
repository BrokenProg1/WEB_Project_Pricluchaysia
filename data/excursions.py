import sqlalchemy

from data.db_session import DeclaratingDataBase


class Excursion(DeclaratingDataBase):
    __tablename__ = 'excursions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True)


    def __repr__(self):
        return f"""<Excursion> Name: {self.title or "No_name"} Price per person: {self.price}"""