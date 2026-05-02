# OUTER MODULES:
import os
import datetime
import requests

from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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
from forms.excursions_edit import EditExc
from forms.excursion_adding import AddiExc
# REST-ful API
from REST_ful_api import users_resources, excursions_resouces, tickets_resources, comments_resources
# END

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # подумать над заменой CSRF-ключа в далёком будущем
app.config['UPLOAD_FOLDER'] = './static/images/'
maps_server_address = 'https://static-maps.yandex.ru/v1?'
maps_api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'  # сменить в будущем
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
        'role': current_user.role
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

# EXCURSIONS
@app.route('/excursions', methods=["GET", "POST"])
def excursions():
    db_sess = db_session.create_session()
    excursions = db_sess.query(Excursion).all()
    parameters = {
        'title': 'Экскурсии',
        'excursions': excursions,
        'role': current_user.role
    }
    return render_template('excursions.html', **parameters)


@app.route('/excursions/<int:exc_id>', methods=["GET", "POST"])
def one_excursion(exc_id):
    db_sess = db_session.create_session()
    excursion = db_sess.query(Excursion).filter(Excursion.id == exc_id).first()
    comments = db_sess.query(Comment).filter(Comment.id_event == excursion.id).all()
    parameters = {
        'title': excursion.title,
        'excursion': excursion,
        'comments': comments
    }
    return render_template('inside_of_exc.html', **parameters)


@app.route('/watching_excs', methods=["GET", "POST"])
def watching_excs():
    db_sess = db_session.create_session()
    excursions = db_sess.query(Excursion).all()
    parameters = {
        'title': 'Просмотр экскурсий гидами и администраторами',
        'excursions': excursions,
        'user': current_user
    }
    return render_template('watching_excs.html', **parameters)


@app.route('/excursions_edit/<int:exc_id>', methods=["GET", "POST"])
def excursions_edit(exc_id):
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    form = EditExc()
    db_sess = db_session.create_session()
    if request.method == "GET":
        exc = db_sess.query(Excursion).filter(Excursion.id == exc_id).first()
        if exc:
            form.title.data = exc.title
            form.description.data = exc.description
            form.price.data = exc.price
            form.img.data = exc.img
            form.way.data = exc.way
            print(exc.way)
            form.img_way = exc.img_way
        else:
            abort(404)
    if form.validate_on_submit():
        exc = db_sess.query(Excursion).filter(Excursion.id == exc_id).first()
        if exc:
            exc.title = form.title.data
            exc.description = form.description.data
            exc.price = form.price.data
            img_file = form.img.data
            exc.way = form.way.data
            img_w = form.img_way
            if img_file and img_file.filename != '':
                filename = secure_filename(img_file.filename)
                if filename:
                    if exc.img:
                        old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                                exc.img.replace('./static/images/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename}"

                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    img_file.save(filepath)
                    exc.img = f"static/images/{unique_filename}"

                toponims = []
                print(exc.way)
                i = '0' + 0
                for toponim in toponims:
                    params_for_map = {
                        'apikey': maps_api_key,
                        'spn': '0.005,0.005'
                    }
                    response = requests.get(maps_server_address, params=params_for_map)
                    toponims.append(response.json())
                # остановка: превращаю строку с точками маршрута в список
                filename_w = secure_filename(img_w.filename)
                if filename_w:
                    if exc.img_way:
                        old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                                exc.img_way.replace('./static/images/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    unique_filename_w = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename_w}"

                    filepath_w = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename_w)
                    img_w.save(filepath_w)
                    exc.img_way = f"static/images/{unique_filename_w}"
            db_sess.commit()
            return redirect('/watching_excs')
        else:
            abort(404)
    return render_template('excursions_edit.html',
                           form=form
                           )


@app.route('/excursions_del/<int:exc_id>', methods=["GET", "POST"])
def excursions_del(exc_id):
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    db_sess = db_session.create_session()
    exc = db_sess.query(Excursion).filter(Excursion.id == exc_id).first()
    if exc:
        db_sess.delete(exc)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/watching_excs')


@app.route('/adding_excs', methods=["GET", "POST"])
def adding_excs():
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    form = AddiExc()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        exc = Excursion()
        exc.title = form.title.data
        exc.description = form.description.data
        exc.price = form.price.data
        img_file = form.img.data
        if img_file and img_file.filename != '':
            filename = secure_filename(img_file.filename)
            if filename:
                if exc.img:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                            exc.img.replace('./static/images/', ''))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename}"

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                img_file.save(filepath)
                exc.img = f"static/images/{unique_filename}"
        db_sess.add(exc)
        db_sess.commit()
        return redirect('/watching_excs')
    return render_template('adding_excs.html', form=form)
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
    exc1.description = 'Just an excursion'
    exc1.img = None
    exc1.price = 100
    exc1.way = '"Светланская улица, 89, Владивосток","улица Володарского, 27, Владивосток"'
    exc1.img_way = None
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