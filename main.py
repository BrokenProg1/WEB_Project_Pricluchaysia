import os
import datetime
import requests

from flask import *

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime

from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from flask_restful import abort, Api

from PIL import Image

from io import BytesIO

from waitress import serve

from data import db_session
from data.users import User
from data.excursions import Excursion
from extras.db_script_for_debugging import function_for_db_debugging
from extras.db_script_for_initialization import function_for_db_initialization

from forms.registration import RegistrationForm
from forms.login import LoginForm
from forms.excursions_edit import EditExc
from forms.excursion_adding import AddiExc
from forms.booking_on_an_exc import BookOnAnExc
from forms.write_comment import WriteComment

from REST_ful_api import (users_resources,
                          excursions_resouces,
                          tickets_resources,
                          comments_resources,
                          reglog_resources)

from extras.functions import secure_change_to_user

from extras.app import Pricluchaysia


app = Flask(__name__)
api = Api(app)
application = Pricluchaysia(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Получение объекта пользователя
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/', methods=["GET", "POST"])
@app.route('/login', methods=["GET", "POST"])
def login_page():
    # Страница авторизации
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
    # Функция выхода из своего аккаунта
    logout_user()
    return redirect("/")


@app.route('/register', methods=["GET", "POST"])
def registration_page():
    # Страница регистрации новых пользователей
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password_field.data != form.password_again_field.data:
            return render_template('register.html', title='Регистрация нового пользователя',
                                   form=form,
                                   message="Пароли не совпадают")
        requests.post(f'{application.protocols[0]}://{application.host_name}/api/register', json={
            'email': form.email_field.data,
            'login': form.username_field.data,
            'password': form.password_field.data
        })
        return redirect('/')
    return render_template('register.html', title='Регистрация нового пользователя', form=form)


@app.route('/main', methods=["GET", "POST"])
@login_required
def main_page():
    # Главная страница сервиса
    secure_change_to_user()
    parameters = {
        'title': 'Главная страница',
        'image': url_for('static', filename='images/THEREISNOPHOTO.png'),
        'about': ' '.join(open('static/files/about.txt', 'r').readlines()),
        'role': current_user.role
    }
    return render_template('main.html', **parameters)


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile_page():
    # Страница профиля конкретного пользователя
    secure_change_to_user()
    user = requests.get(f'{application.protocols[0]}://{application.host_name}/api/users/{current_user.id}').json()['user']
    all_tics = requests.get(f'{application.protocols[0]}://{application.host_name}/api/tickets').json()['tickets']
    tickets = [x for x in all_tics if x['id_user'] == current_user.id]
    parameters = {
        'title': f"Профиль пользователя {user['login']}",
        'user': user,
        'tickets': tickets,
        'has_tics': len(tickets) > 0
    }
    return render_template('profile.html', **parameters)


@app.route('/excursions', methods=["GET"])
@login_required
def watching_excursions_page():
    # Страница просмотра экскурсий для всех категорий пользователей: обычных, гидов и администраторов
    secure_change_to_user()
    excursions = requests.get(f'{application.protocols[0]}://{application.host_name}/api/excursions').json()['excursions']
    parameters = {
        'title': 'Экскурсии',
        'excursions': excursions,
        'are_excs_exist': len(excursions) > 0,
        'role': current_user.role
    }
    return render_template('excursions.html', **parameters)


@app.route('/excursions/<int:exc_id>', methods=["GET", "POST", "DELETE"])
@login_required
def watching_one_excursion_page(exc_id):
    # Просмотр отзывов под конкретной экскурсией
    secure_change_to_user()
    form = WriteComment()

    if request.method == 'GET':
        resp = requests.get(f'{application.protocols[0]}://{application.host_name}/api/excursions/{exc_id}')

        data = resp.json()
        excursion = data['excursion']

        resp = requests.get(f'{application.protocols[0]}://{application.host_name}/api/comments')
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
        requests.post(f'{application.protocols[0]}://{application.host_name}/api/comments', json=new_comment)

        return redirect(f'/excursions/{exc_id}')


@app.route('/watching_excs', methods=["GET"])
@login_required
def watching_excursions_page_for_privileged():
    # Страница для просмотра экскурсий только для привилегированных пользователей, администраторов и гидов,
    # с соответствующим функционалом
    secure_change_to_user()
    excursions = requests.get(f'{application.protocols[0]}://{application.host_name}/api/excursions').json()['excursions']
    parameters = {
        'title': 'Просмотр экскурсий гидами и администраторами',
        'excursions': excursions,
        'are_excs_exist': len(excursions) > 0,
        'user': current_user
    }
    return render_template('watching_excs.html', **parameters)


@app.route('/excursions_edit/<int:exc_id>', methods=["GET", "POST"])
@login_required
def editing_excursions_page(exc_id):
    # Страница для изменения экскурсий
    secure_change_to_user()
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    form = EditExc()
    db_sess = db_session.create_session()
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
                    old_path = os.path.join(application.app.config['UPLOAD_FOLDER'],
                                            exc.img.replace('./static/images/', ''))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename}"

                filepath = os.path.join(application.app.config['UPLOAD_FOLDER'], unique_filename)
                img_file.save(filepath)
                exc.img = f"static/images/{unique_filename}"
            else:
                exc.img = '0'

        toponyms = []
        entering = [s.strip('"') for s in exc.way.split('","')]
        for toponym in entering:
            params_for_map = {
                'apikey': application.geocoder_api_key,
                'geocode': toponym,
                'format': 'json'
            }
            response = requests.get(application.geocoder_api_server, params=params_for_map)
            toponyms.append(response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos'])
        center = (sum([float(x.split()[0]) for x in toponyms]) / len(toponyms),
                  sum([float(y.split()[1]) for y in toponyms]) / len(toponyms))
        map_params = {
            "ll": ','.join([str(center[0]), str(center[1])]),
            "spn": '0.15,0.15',
            "apikey": application.maps_api_key,
            'pt': '~'.join([f'{t.split(',')[0]},{t.split(',')[1]},pm2rdm' for t in [",".join(p.split()) for p in toponyms]]),
            'format': 'biz'
        }
        response = requests.get(application.maps_server_address, params=map_params)
        im = BytesIO(response.content)

        if exc.img_way:
            old_path = os.path.join(application.app.config['UPLOAD_FOLDER'],
                                    exc.img_way.replace('./static/images/', ''))
            if os.path.exists(old_path):
                os.remove(old_path)
        unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

        filepath = os.path.join(application.app.config['UPLOAD_FOLDER'], unique_filename)
        Image.open(im).save(filepath)
        exc.img_way = f"static/images/{unique_filename}"

        db_sess.commit()
        return redirect('/watching_excs')
    return render_template('excursions_edit.html',
                           form=form
                           )


@app.route('/excursions_del/<int:exc_id>', methods=["GET", "POST"])
@login_required
def deleting_excursions_page(exc_id):
    # Обработчик удаления экскурсий
    secure_change_to_user()
    if current_user.role not in ['guide', 'administrator']:
        return redirect('/main')
    exc = requests.get(f'{application.protocols[0]}://{application.host_name}/api/excursions/{exc_id}').json()
    if exc:
        try:
            os.remove(exc['excursion']['img'])
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        try:
            os.remove(exc['excursion']['img_way'])
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        requests.delete(f'{application.protocols[0]}://{application.host_name}/api/excursions/{exc_id}')
    else:
        abort(404)
    return redirect('/watching_excs')


@app.route('/adding_excs', methods=["GET", "POST"])
@login_required
def adding_excursions_page():
    # Страница добавления экскурсий
    secure_change_to_user()
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

        filename = secure_filename(img_file.filename)
        if filename:
            if new_excursion.get('img', 0) == 0:
                old_path = os.path.join(application.app.config['UPLOAD_FOLDER'],
                                        new_excursion['img'].replace('./static/images/', ''))
                if os.path.exists(old_path):
                    os.remove(old_path)
            unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename}"

            filepath = os.path.join(application.app.config['UPLOAD_FOLDER'], unique_filename)
            img_file.save(filepath)
            new_excursion['img'] = f"static/images/{unique_filename}"
        else:
            new_excursion['img'] = '0'

        toponyms = []
        entering = [s.strip('"') for s in new_excursion['way'].split('","')]
        for toponym in entering:
            params_for_map = {
                'apikey': application.geocoder_api_key,
                'geocode': toponym,
                'format': 'json'
            }
            response = requests.get(application.geocoder_api_server, params=params_for_map)
            toponyms.append(
                response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos'])
        center = (sum([float(x.split()[0]) for x in toponyms]) / len(toponyms),
                  sum([float(y.split()[1]) for y in toponyms]) / len(toponyms))
        map_params = {
            "ll": ','.join([str(center[0]), str(center[1])]),
            "spn": '0.15,0.15',
            "apikey": application.maps_api_key,
            'pt': '~'.join(
                [f'{t.split(',')[0]},{t.split(',')[1]},pm2rdm' for t in [",".join(p.split()) for p in toponyms]]),
            'format': 'biz'
        }
        response = requests.get(application.maps_server_address, params=map_params)
        im = BytesIO(response.content)

        if new_excursion.get('img_way', 0) == 0:
            old_path = os.path.join(application.app.config['UPLOAD_FOLDER'],
                                    new_excursion['img_way'].replace('./static/images/', ''))
            if os.path.exists(old_path):
                os.remove(old_path)
        unique_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

        filepath = os.path.join(application.app.config['UPLOAD_FOLDER'], unique_filename)
        Image.open(im).save(filepath)
        new_excursion['img_way'] = f"static/images/{unique_filename}"

        new_excursion['way'] = form.way.data

        requests.post(f'{application.protocols[0]}://{application.host_name}/api/excursions', json=new_excursion)

        return redirect('/watching_excs')
    return render_template('adding_excs.html', form=form)


@app.route('/book_on_an_exc/<int:exc_id>', methods=["GET", "POST"])
@login_required
def booking_on_an_excursion_page(exc_id):
    # Страница для записи на экскурсии
    secure_change_to_user()
    form = BookOnAnExc()

    exc = requests.get(f"{application.protocols[0]}://{application.host_name}/api/excursions/{exc_id}").json()['excursion']
    if not exc:
        abort(404)
    if request.method == 'POST':
        if form.count_of_people.data < 1:
            abort(400)

        is_there_a_tic = requests.get(f"{application.protocols[0]}://{application.host_name}/api/tickets").json()['tickets']
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

        requests.post(f"{application.protocols[0]}://{application.host_name}/api/tickets", json=new_ticket)

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


@app.route('/comments_del/<int:com_id>/<int:exc_id>/<is_him>', methods=['GET', 'DELETE'])
@login_required
def deleting_comments_page(com_id, exc_id, is_him):
    # Обработчик удаления отзывов под экскурсиями
    secure_change_to_user()
    if current_user.role not in ["administrator"]:
        if is_him == 'False':
            return redirect('/main')

    requests.delete(f'{application.protocols[0]}://{application.host_name}/api/comments/{com_id}')

    return redirect(f'/excursions/{exc_id}')


@app.route('/watching_users', methods=['GET', "POST"])
@login_required
def watching_users_and_editing_permissions_page():
    # Страница для просмотра всех пользователей администраторами и изменения ими прав всех пользователей
    secure_change_to_user()
    if current_user.role != "administrator":
        return redirect('/main')
    users = requests.get(f"{application.protocols[0]}://{application.host_name}/api/users").json()['users']
    restructure_by_role = {
        'USERS': [x for x in users if x['role'] == 'user'],
        'GUIDES': [x for x in users if x['role'] == 'guide']
    }
    if request.method == "GET":
        pass
    elif request.method == "POST":
        change_list = [(change_to, int(id_)) for change_to, id_ in request.form.items()]
        ids = set([x[1] for x in change_list])

        if len(change_list) != len(ids):
            abort(400, message='Одному пользователю дважды меняют права')

        changes = {x[1]: x[0] for x in change_list}

        db_sess = db_session.create_session()
        userss = db_sess.query(User).filter(User.role != 'administrator').all()

        for user in userss:
            if user.id in ids:
                user.role = changes[user.id]

        db_sess.commit()
        db_sess.close()
        return redirect('/watching_users')

    return render_template('watching_users.html', users=users, roles=restructure_by_role)


if __name__ == '__main__':
    # Инициализация приложения
    db_session.global_init("db/databaseFile.db")

    api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(excursions_resouces.ExcursionsResource, '/api/excursions/<int:exc_id>')
    api.add_resource(excursions_resouces.ExcursionsListResource, '/api/excursions')
    api.add_resource(tickets_resources.TicketsResource, '/api/tickets/<int:tic_id>')
    api.add_resource(tickets_resources.TicketsListResource, '/api/tickets')
    api.add_resource(comments_resources.CommentsResource, '/api/comments/<int:com_id>')
    api.add_resource(comments_resources.CommentsListResource, '/api/comments')
    api.add_resource(reglog_resources.RegisterResource, '/api/register')

    if application.mod == 'debug':
        function_for_db_debugging()
    function_for_db_initialization()

    serve(app, host='0.0.0.0', port=5000)