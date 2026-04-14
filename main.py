from flask import *
from werkzeug.security import generate_password_hash

from data import db_session
from data.db_session import create_session
from data.users import User
from data.excursions import Excursion
from data.tickets import Ticket
from data.comments import Comment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # подумать над заменой CSRF-ключа в далёком будущем


@app.route('/', methods=["GET"])
def main_page():
    return render_template('base.html', title='Main Page')


if __name__ == '__main__':
    db_session.global_init("db/databaseFile.db")
    session = db_session.create_session()

    # users
    user = User()
    user.login = 'log_1'
    user.email = 'user1@user.user'
    user.hashed_password = generate_password_hash('123')
    user.role = 'user'
    session.add(user)

    user = User()
    user.login = 'log_2'
    user.email = 'user2@user.user'
    user.hashed_password = generate_password_hash('123')
    user.role = 'user'
    session.add(user)

    user = User()
    user.login = 'log_3'
    user.email = 'user3@user.user'
    user.hashed_password = generate_password_hash('123')
    user.role = 'guide'
    session.add(user)

    user = User()
    user.login = 'log_4'
    user.email = 'user4@user.user'
    user.hashed_password = generate_password_hash('123')
    user.role = 'administrator'
    session.add(user)
    # end
    # excursions
    exc = Excursion()
    exc.title = 'exc_1'
    exc.description = 'Just an excursion'
    exc.img = None
    exc.price = 100
    session.add(exc)
    # end
    # tickets
    tic = Ticket()
    tic.id_event = 1
    tic.name_event = 'exc_1'
    tic.price_event = 100
    tic.id_user = 1
    tic.name = 'log_1'
    tic.count_of_people = 1
    session.add(tic)

    tic = Ticket()
    tic.id_event = 1
    tic.name_event = 'exc_1'
    tic.price_event = 100
    tic.id_user = 2
    tic.name = 'log_2'
    tic.count_of_people = 3
    session.add(tic)
    # end
    # comments
    com = Comment()
    com.id_event = 1
    com.id_user = 1
    com.name_user = 'log_1'
    com.role_user = 'user'
    com.text = 'I enjoyed by the guide!'
    com.date = '32.13.2099'
    session.add(com)
    # end
    session.commit()

    app.run(debug=True)