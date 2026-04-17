# outer modules
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# inner modules
# DATABASES
from data import db_session
from data.users import User
from data.excursions import Excursion
from data.tickets import Ticket
from data.comments import Comment
# FORMS
from forms.registration import RegistrationForm
from  forms.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # подумать над заменой CSRF-ключа в далёком будущем


@app.route('/register', methods=["GET", "POST"])
def registration_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password_field.data != form.password_again_field.data:
            return render_template('registration.html', title='Регистрация нового пользователя',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email_field.data).first():
            return render_template('registration.html', title='Регистрация нового пользователя',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            login=form.username_field.data,
            email=form.email_field.data,
            role='user'
        )
        user.set_password(form.password_field.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация нового пользователя', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/', methods=["GET"])
def main_page():
    return render_template('main.html', title='Главная страница')


if __name__ == '__main__':
    db_session.global_init("db/databaseFile.db")
    session = db_session.create_session()

    session.query(Comment).delete()
    session.query(Ticket).delete()
    session.query(Excursion).delete()
    session.query(User).delete()

    # users
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
    # end
    # excursions
    exc1 = Excursion()
    exc1.title = 'exc_1'
    exc1.description = 'Just an excursion'
    exc1.img = None
    exc1.price = 100
    session.add(exc1)
    # end
    # tickets
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
    # end
    # comments
    com1 = Comment()
    com1.id_event = 1
    com1.id_user = 1
    com1.name_user = 'log_1'
    com1.role_user = 'user'
    com1.text = 'I enjoyed by the guide!'
    com1.date = datetime(2025, 12, 31)
    session.add(com1)
    # end
    session.commit()
    session.close()

    app.run(debug=True)