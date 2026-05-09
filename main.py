# OUTER MODULES:
import os
import datetime
import requests
import pprint
import json

from flask import *
from flask_wtf import form
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_restful import reqparse, abort, Api, Resource
from PIL import Image
from io import BytesIO
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
from forms.booking_on_an_exc import BookOnAnExc
from forms.write_comment import WriteComment
# REST-ful API:
from REST_ful_api import (users_resources,
                          excursions_resouces,
                          tickets_resources,
                          comments_resources,
                          reglog_resources)
# END

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # подумать над заменой CSRF-ключа в далёком будущем
app.config['UPLOAD_FOLDER'] = './static/images/'
maps_server_address = 'https://static-maps.yandex.ru/v1?'
maps_api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
geocoder_api_server = "https://geocode-maps.yandex.ru/1.x/"
geocoder_api_key = '8013b162-6b42-4997-9691-77b7074026e0'  # сменить в будущем
login_manager = LoginManager()
login_manager.init_app(app)
host_name = 'localhost:5000'

# -----L O G I N-----
@login_manager.user_loader
# can`t be REST-fulled
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)
    # Здесь можно было бы использовать:
    # requests.get(f'http://{host_name}/api/users/{user_id}').json()['user'] ,
    # но возвращается словарь, а не объект
    # Я пытался создать свой типо словарь, который мог бы обращаться к атрибутам как к ключам,
    # и из ответа перебросить данные туда, но атрибуты пользователя, создающиеся в объекте изначально,
    # я не получал, поэтому вернулся к ORM
    """
    user = requests.get(f'http://{host_name}/api/users/{user_id}').json()['user']
    return special_dict(
        email=user['email'],
        id=user['id'],
        login=user['login'],
        role=user['role']
    )
    """


@app.route('/', methods=["GET", "POST"])
@app.route('/login', methods=["GET", "POST"])
# попросить о помощи с типами данных
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email_field.data).first()
        if user and check_password_hash(user.hashed_password, form.password_field.data):
            login_user(user)
            return redirect('/main')
        """requests.post(f'http://{host_name}/api/login', json={
            'email': form.email_field.data,
            'password': form.password_field.data,
            'login': form.username_field.data
        })

        return redirect('/main')"""
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout', methods=["GET", "POST"])
@login_required
# can`t be REST-fulled
def logout():
    logout_user()
    return redirect("/")
# -----E N D-----
# -----R E G I S T R A T I O N-----
@app.route('/register', methods=["GET", "POST"])
# REST-fulled
def registration_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password_field.data != form.password_again_field.data:
            return render_template('register.html', title='Регистрация нового пользователя',
                                   form=form,
                                   message="Пароли не совпадают")
        requests.post(f'http://{host_name}/api/register', json={
            'email': form.email_field.data,
            'login': form.username_field.data,
            'password': form.password_field.data
        })

        return redirect('/')
    return render_template('register.html', title='Регистрация нового пользователя', form=form)
# -----E N D-----
# -----P A G E S-----
@app.route('/main', methods=["GET", "POST"])
@login_required
# can`t be REST-fulled
def main_page():
    parameters = {
        'title': 'Главная страница',
        'image': url_for('static', filename='images/THEREISNOPHOTO.png'),
        'about': ' '.join(open('static/files/about.txt', 'r').readlines()),
        'role': current_user.role
    }
    return render_template('main.html', **parameters)


@app.route('/profile', methods=["GET", "POST"])
@login_required
# REST-fulled
def profile_page():
    user = requests.get(f'http://{host_name}/api/users/{current_user.id}').json()['user']
    all_tics = requests.get(f'http://{host_name}/api/tickets').json()['tickets']
    tickets = [x for x in all_tics if x['id_user'] == current_user.id]
    parameters = {
        'title': f'Профиль пользователя {user['login']}',
        'user': user,
        'tickets': tickets,
        'has_tics': len(tickets) > 0
    }
    return render_template('profile.html', **parameters)

# EXCURSIONS
@app.route('/excursions', methods=["GET"])
@login_required
# REST-fulled
def excursions():  # для всех пользователей
    excursions = requests.get(f'http://{host_name}/api/excursions').json()['excursions']
    parameters = {
        'title': 'Экскурсии',
        'excursions': excursions,
        'role': current_user.role
    }
    return render_template('excursions.html', **parameters)


@app.route('/excursions/<int:exc_id>', methods=["GET", "POST", "DELETE"])
@login_required
# REST-fulled
def one_excursion(exc_id):
    form = WriteComment()

    if request.method == 'GET':
        resp = requests.get(f'http://{host_name}/api/excursions/{exc_id}')

        data = resp.json()
        excursion = data['excursion']

        resp = requests.get(f'http://{host_name}/api/comments')
        data = resp.json()
        all_comments = data['comments']

        return render_template('inside_of_exc.html',
                               excursion=excursion,
                               comments=all_comments,
                               user=current_user,
                               exc_id=exc_id,
                               writecom=form)

    elif request.method == 'POST':
        new_comment = {
            'id_event': exc_id,
            'id_user': current_user.id,
            'name_user': current_user.login,
            'role_user': current_user.role,
            'text': form.comment.data,
            'date': str(datetime.today())
        }
        requests.post('http://localhost:5000/api/comments', json=new_comment)

        return redirect(f'/excursions/{exc_id}')


@app.route('/watching_excs', methods=["GET"])
@login_required
# REST-fulled
def watching_excs():  # для привилегированных пользователей
    excursions = requests.get(f'http://{host_name}/api/excursions').json()['excursions']
    print(excursions)
    parameters = {
        'title': 'Просмотр экскурсий гидами и администраторами',
        'excursions': excursions,
        'user': current_user
    }
    return render_template('watching_excs.html', **parameters)


@app.route('/excursions_edit/<int:exc_id>', methods=["GET", "POST", "PUT"])
@login_required
# попросить о помощи с put-запросом
def excursions_edit(exc_id):
    global form
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    form = EditExc()

    exc = requests.get(f'http://{host_name}/api/excursions/{exc_id}').json()['excursion']
    if not exc:
        abort(404)

    if request.method == "GET":
        form.title.data = exc['title']
        form.description.data = exc['description']
        form.price.data = exc['price']
        form.way.data = exc['way']
    return render_template('excursions_edit.html',
                           form=form, exc_id=exc_id
                           )

    """db_sess = db_session.create_session()
    exc = db_sess.query(Excursion).filter(Excursion.id == exc_id).first()
    if not exc:
        abort(404)

    if request.method == "GET":
        form.title.data = exc.title
        form.description.data = exc.description
        form.price.data = exc.price
        form.img.data = exc.img
        form.way.data = exc.way
        form.img_way = exc.img_way
    if form.validate_on_submit():
        exc.title = form.title.data
        exc.description = form.description.data
        exc.price = form.price.data
        img_file = form.img.data
        exc.way = form.way.data
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

        toponyms = []
        entering = [s.strip('"') for s in exc.way.split('","')]
        for toponym in entering:
            params_for_map = {
                'apikey': geocoder_api_key,
                'geocode': toponym,
                'format': 'json'
            }
            response = requests.get(geocoder_api_server, params=params_for_map)
            toponyms.append(response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos'])
        center = (sum([float(x.split()[0]) for x in toponyms]) / len(toponyms),
                  sum([float(y.split()[1]) for y in toponyms]) / len(toponyms))
        map_params = {
            "ll": ','.join([str(center[0]), str(center[1])]),
            "spn": '0.005,0.005',
            "apikey": maps_api_key,
            'pt': '~'.join([f'{t.split(',')[0]},{t.split(',')[1]},pm2rdm' for t in [",".join(p.split()) for p in toponyms]]),
            'format': 'biz'
        }
        response = requests.get(maps_server_address, params=map_params)
        im = BytesIO(response.content)

        if exc.img_way:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                    exc.img_way.replace('./static/images/', ''))
            if os.path.exists(old_path):
                os.remove(old_path)
        unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        Image.open(im).save(filepath)
        exc.img_way = f"static/images/{unique_filename}"

        db_sess.commit()
        return redirect('/watching_excs')
    return render_template('excursions_edit.html',
                           form=form
                           )"""


@app.route('/excursions_put/<int:exc_id>', methods=['GET', 'PUT'])
@login_required
# поросить о помощи с put-запросом
def excursions_put(exc_id):
    global form

    # ////////
    new_excursion = {
        'title': form.title.data,
        'description': form.description.data,
        'price': form.price.data,
        'way': form.way.data,
        'img': form.img.data,
        'img_way': ''
    }

    img_file = form.img.data

    if img_file and img_file.filename != '':
        filename = secure_filename(img_file.filename)
        if filename:
            if new_excursion.get('img', 0) == 0:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        new_excursion['img'].replace('./static/images/', ''))
                if os.path.exists(old_path):
                    os.remove(old_path)
            unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename}"

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            img_file.save(filepath)
            new_excursion['img'] = f"static/images/{unique_filename}"

    toponyms = []
    entering = [s.strip('"') for s in new_excursion['way'].split('","')]
    for toponym in entering:
        params_for_map = {
            'apikey': geocoder_api_key,
            'geocode': toponym,
            'format': 'json'
        }
        response = requests.get(geocoder_api_server, params=params_for_map)
        toponyms.append(
            response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos'])
    center = (sum([float(x.split()[0]) for x in toponyms]) / len(toponyms),
              sum([float(y.split()[1]) for y in toponyms]) / len(toponyms))
    map_params = {
        "ll": ','.join([str(center[0]), str(center[1])]),
        "spn": '0.01,0.01',
        "apikey": maps_api_key,
        'pt': '~'.join(
            [f'{t.split(',')[0]},{t.split(',')[1]},pm2rdm' for t in [",".join(p.split()) for p in toponyms]]),
        'format': 'biz'
    }
    response = requests.get(maps_server_address, params=map_params)
    im = BytesIO(response.content)

    if new_excursion.get('img_way', 0) == 0:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                new_excursion['img_way'].replace('./static/images/', ''))
        if os.path.exists(old_path):
            os.remove(old_path)
    unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    Image.open(im).save(filepath)
    new_excursion['img_way'] = f"static/images/{unique_filename}"

    new_excursion['way'] = form.way.data
    # ////////

    print('putting')
    requests.put(f'http://{host_name}/api/excursions', json=new_excursion)
    print('putted')

    return redirect('/watching_excs')


@app.route('/excursions_del/<int:exc_id>', methods=["GET", "POST"])
@login_required
# REST-fulled
def excursions_del(exc_id):
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    exc = requests.get(f'http://{host_name}/api/excursions/{exc_id}').json()['excursion']
    if exc:
        try:
            os.remove(exc.img)
        except Exception:
            pass
        try:
            os.remove(exc.img_way)
        except Exception:
            pass
        requests.delete(f'http://{host_name}/api/excursions/{exc_id}')
    else:
        abort(404)
    return redirect('/watching_excs')


@app.route('/adding_excs', methods=["GET", "POST"])
@login_required
# REST-fulled
def adding_excs():
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    form = AddiExc()
    if request.method == "POST":
        new_excursion = {
            'title': form.title.data,
            'description': form.description.data,
            'price': form.price.data,
            'way': form.way.data,
            'img': form.img.data,
            'img_way': ''
        }

        img_file = form.img.data

        if img_file and img_file.filename != '':
            filename = secure_filename(img_file.filename)
            if filename:
                if new_excursion.get('img', 0) == 0:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                            new_excursion['img'].replace('./static/images/', ''))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename}"

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                img_file.save(filepath)
                new_excursion['img'] = f"static/images/{unique_filename}"

        toponyms = []
        entering = [s.strip('"') for s in new_excursion['way'].split('","')]
        for toponym in entering:
            params_for_map = {
                'apikey': geocoder_api_key,
                'geocode': toponym,
                'format': 'json'
            }
            response = requests.get(geocoder_api_server, params=params_for_map)
            toponyms.append(
                response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos'])
        center = (sum([float(x.split()[0]) for x in toponyms]) / len(toponyms),
                  sum([float(y.split()[1]) for y in toponyms]) / len(toponyms))
        map_params = {
            "ll": ','.join([str(center[0]), str(center[1])]),
            "spn": '0.01,0.01',
            "apikey": maps_api_key,
            'pt': '~'.join(
                [f'{t.split(',')[0]},{t.split(',')[1]},pm2rdm' for t in [",".join(p.split()) for p in toponyms]]),
            'format': 'biz'
        }
        response = requests.get(maps_server_address, params=map_params)
        im = BytesIO(response.content)

        if new_excursion.get('img_way', 0) == 0:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                    new_excursion['img_way'].replace('./static/images/', ''))
            if os.path.exists(old_path):
                os.remove(old_path)
        unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        Image.open(im).save(filepath)
        new_excursion['img_way'] = f"static/images/{unique_filename}"

        new_excursion['way'] = form.way.data

        requests.post(f'http://{host_name}/api/excursions', json=new_excursion)

        return redirect('/watching_excs')
    return render_template('adding_excs.html', form=form)

    """db_sess = db_session.create_session()
    if form.validate_on_submit():
        exc = Excursion()
        exc.title = form.title.data
        exc.description = form.description.data
        exc.price = form.price.data
        img_file = form.img.data
        exc.way = form.way.data
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

        toponyms = []
        entering = [s.strip('"') for s in exc.way.split('","')]
        for toponym in entering:
            params_for_map = {
                'apikey': geocoder_api_key,
                'geocode': toponym,
                'format': 'json'
            }
            response = requests.get(geocoder_api_server, params=params_for_map)
            toponyms.append(response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos'])
        center = (sum([float(x.split()[0]) for x in toponyms]) / len(toponyms),
                  sum([float(y.split()[1]) for y in toponyms]) / len(toponyms))
        map_params = {
            "ll": ','.join([str(center[0]), str(center[1])]),
            "spn": '0.005,0.005',
            "apikey": maps_api_key,
            'pt': '~'.join([f'{t.split(',')[0]},{t.split(',')[1]},pm2rdm' for t in [",".join(p.split()) for p in toponyms]]),
            'format': 'biz'
        }
        response = requests.get(maps_server_address, params=map_params)
        im = BytesIO(response.content)

        if exc.img_way:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                    exc.img_way.replace('./static/images/', ''))
            if os.path.exists(old_path):
                os.remove(old_path)
        unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        Image.open(im).save(filepath)
        exc.img_way = f"static/images/{unique_filename}"

        db_sess.add(exc)
        db_sess.commit()
        return redirect('/watching_excs')
    return render_template('adding_excs.html', form=form)"""

# TICKETS
@app.route('/book_on_an_exc/<int:exc_id>', methods=["GET", "POST"])
@login_required
# REST-fulled
def book_on_an_exc(exc_id):
    form = BookOnAnExc()

    exc = requests.get(f"http://{host_name}/api/excursions/{exc_id}").json()['excursion']
    if not exc:
        abort(404)
    if request.method == 'POST':
        if form.count_of_people.data < 1:
            abort(400)

        is_there_a_tic = requests.get(f"http://{host_name}/api/tickets").json()['tickets']
        for tic in is_there_a_tic:
            if tic['id_event'] == exc_id and \
            tic['id_user'] == current_user.id and \
            tic['count_of_people'] == form.count_of_people.data:
                abort(409)

        new_ticket = {
            'id_event': exc_id,
            'name_event': exc['title'],
            'price_event': exc['price'],
            'id_user': current_user.id,
            'name_user': current_user.login,
            'count_of_people': form.count_of_people.data
        }

        requests.post(f"http://{host_name}/api/tickets", json=new_ticket)

        if current_user.role == "user":
            return redirect('/excursions')
        if current_user.role == "administrator" or current_user.role == "guide":
            return redirect('/watching_excs')

    parameters = {
        'title': f'Запись на экскурию {exc['title']}',
        'exc': exc,
        'user': current_user,
        'form': form
    }
    return render_template('book_on_an_exc.html', **parameters)

# COMMENTS
@app.route('/comments_del/<int:com_id>/<int:exc_id>', methods=['GET', 'DELETE'])
@login_required
# REST-fulled
def comments_del(com_id, exc_id):
    if current_user.role not in ["guide", "administrator"]:
        return redirect('/main')

    requests.delete(f'http://{host_name}/api/comments/{com_id}')

    return redirect(f'/excursions/{exc_id}')
# -----E N D-----
# -----T U R N I N G _ O N-----
if __name__ == '__main__':
    db_session.global_init("db/databaseFile.db")
    session = db_session.create_session()

    api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(excursions_resouces.ExcursionsResource, '/api/excursions/<int:exc_id>')
    api.add_resource(excursions_resouces.ExcursionsListResource, '/api/excursions')
    api.add_resource(tickets_resources.TicketsResource, '/api/tickets/<int:tic_id>')
    api.add_resource(tickets_resources.TicketsListResource, '/api/tickets')
    api.add_resource(comments_resources.CommentsResource, '/api/comments/<int:com_id>')
    api.add_resource(comments_resources.CommentsListResource, '/api/comments')
    api.add_resource(reglog_resources.RegisterResource, '/api/register')
    api.add_resource(reglog_resources.LoginResource, '/api/login')

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
    com1.date = str(datetime(2025, 12, 31))
    session.add(com1)
    # end
    session.commit()
    session.close()

    app.run(debug=True)
# -----E N D-----