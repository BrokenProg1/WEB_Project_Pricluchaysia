from werkzeug.security import generate_password_hash

from data import db_session
from data.users import User


def function_for_db_initialization():
    # Функция для создания аккаунта администратора в БД
    session = db_session.create_session()

    user1 = User()
    user1.login = 'administrator'
    user1.email = 'inner@ineer.ru'
    user1.hashed_password = generate_password_hash('administrators_pswd')
    user1.role = 'administrator'
    session.add(user1)

    session.commit()
    session.close()