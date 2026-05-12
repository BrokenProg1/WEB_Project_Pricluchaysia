from datetime import datetime

from werkzeug.security import generate_password_hash

from data import db_session
from data.comments import Comment
from data.excursions import Excursion
from data.tickets import Ticket
from data.users import User


def function_for_db_debugging():
    # Функция для заполния БД данными в режиме работы 'debug'
    session = db_session.create_session()

    session.query(Comment).delete()
    session.query(Ticket).delete()
    session.query(Excursion).delete()
    session.query(User).delete()

    user1 = User()
    user1.login = 'log_1'
    user1.email = 'user1@user.user'
    user1.hashed_password = generate_password_hash('123')
    user1.role = 'user'
    session.add(user1)

    user2 = User()
    user2.login = 'log_2'
    user2.email = 'user2@user.user'
    user2.hashed_password = generate_password_hash('123')
    user2.role = 'user'
    session.add(user2)

    user3 = User()
    user3.login = 'log_3'
    user3.email = 'user3@user.user'
    user3.hashed_password = generate_password_hash('123')
    user3.role = 'guide'
    session.add(user3)

    user4 = User()
    user4.login = 'log_4'
    user4.email = 'user4@user.user'
    user4.hashed_password = generate_password_hash('123')
    user4.role = 'administrator'
    session.add(user4)

    exc1 = Excursion()
    exc1.title = 'exc_1'
    exc1.description = 'Just an excursion'
    exc1.img = None
    exc1.price = 100
    exc1.way = '"Светланская улица, 89, Владивосток","улица Володарского, 27, Владивосток"'
    exc1.img_way = None
    session.add(exc1)

    tic1 = Ticket()
    tic1.id_event = 1
    tic1.name_event = 'exc_1'
    tic1.price_event = 100
    tic1.id_user = 1
    tic1.name_user = 'log_1'
    tic1.count_of_people = 1
    session.add(tic1)

    tic2 = Ticket()
    tic2.id_event = 1
    tic2.name_event = 'exc_1'
    tic2.price_event = 100
    tic2.id_user = 2
    tic2.name_user = 'log_2'
    tic2.count_of_people = 3
    session.add(tic2)

    com1 = Comment()
    com1.id_event = 1
    com1.id_user = 1
    com1.name_user = 'log_1'
    com1.role_user = 'user'
    com1.text = 'I enjoyed by the guide!'
    com1.date = str(datetime(2025, 12, 31))
    session.add(com1)

    session.commit()
    session.close()