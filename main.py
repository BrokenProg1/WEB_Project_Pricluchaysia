# OUTER MODULES:
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_restful import reqparse, abort, Api, Resource
from requests import get, post, delete, put
# END
# INNER MODULES:
# databases:
from data import db_session
from data.users import User
from data.excursions import Excursion
from data.tickets import Ticket
from data.comments import Comment
# forms:
from forms.registration import RegistrationForm
from forms.login import LoginForm
# REST-ful API
from REST_ful_api import users_resources, excursions_resouces, tickets_resources, comments_resources
# END

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # подумать над заменой CSRF-ключа в далёком будущем
login_manager = LoginManager()
login_manager.init_app(app)

# -----L O G I N-----
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/', methods=["GET", "POST"])
@app.route('/login', methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email_field.data).first()
        if user and check_password_hash(user.hashed_password, form.password_field.data):
            login_user(user)
            return redirect('/main')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")
# -----E N D-----
# -----R E G I S T R A T I O N-----
@app.route('/register', methods=["GET", "POST"])
def registration_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password_field.data != form.password_again_field.data:
            return render_template('register.html', title='Регистрация нового пользователя',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email_field.data).first():
            return render_template('register.html', title='Регистрация нового пользователя',
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
        return redirect('/main')
    return render_template('register.html', title='Регистрация нового пользователя', form=form)
# -----E N D-----
# -----P A G E S-----
@app.route('/main', methods=["GET", "POST"])
def main_page():
    parameters = {
        'title': 'Главная страница',
        'image': url_for('static', filename='images/THEREISNOPHOTO.png'),
        'about': ' '.join(open('static/files/about.txt', 'r').readlines()),
    }
    return render_template('main.html', **parameters)


@app.route('/profile', methods=["GET", "POST"])
def profile_page():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    tickets = db_sess.query(Ticket).filter(Ticket.id_user == user.id).all()
    parameters = {
        'title': f'Профиль пользователя {user.login}',
        'user': user,
        'tickets': tickets
    }
    return render_template('profile.html', **parameters)


@app.route('/excursions', methods=["GET", "POST"])
def excursions():
    db_sess = db_session.create_session()
    excursions = db_sess.query(Excursion).all()
    parameters = {
        'title': 'Экскурсии',
        'excursions': excursions
    }
    return render_template('excursions.html', **parameters)
# -----E N D-----
# -----T U R N I N G _ O N-----
if __name__ == '__main__':
    db_session.global_init("db/databaseFile.db")
    session = db_session.create_session()

    api.add_resource(users_resources.UsersResource, '/api/users')
    api.add_resource(users_resources.UsersListResource, '/api/users/<int:user_id>')
    api.add_resource(excursions_resouces.ExcursionsResource, '/api/excursions')
    api.add_resource(excursions_resouces.ExcursionsListResource, '/api/excursions/<int:exc_id>')
    api.add_resource(tickets_resources.TicketsResource, '/api/tickets')
    api.add_resource(tickets_resources.TicketsListResource, '/api/tickets/<int:tic_id>')
    api.add_resource(comments_resources.CommentsResource, '/api/comments')
    api.add_resource(comments_resources.CommentsListResource, '/api/comments/<int:com_id>')

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
    exc1.descryption = 'Just an excursion'
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
# -----E N D-----