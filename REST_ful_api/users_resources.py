from flask import jsonify, abort
from flask_restful import Resource, reqparse
from data.users import User
from data import db_session


parser = reqparse.RequestParser()
parser.add_argument('login', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('email', required=True)
parser.add_argument('role', required=True)


def abort_if_users_not_found(user_id):
    # Если пользователь не найден, то возвращаем код ошибки 404
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404)


class UsersResource(Resource):
    def get(self, user_id):
        # Получаем одного конкретного пользователя
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.close()
        return jsonify({'user':
            {'id': user.id,
             'login': user.login,
             'email': user.email,
             'role': user.role}})

    def delete(self, user_id):
        # Удаляем одного конкретного пользователя
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        # Получаем список всех пользователей
        session = db_session.create_session()
        users = session.query(User).all()
        session.close()
        return jsonify({'users': [
            {'id': item.id,
             'login': item.login,
             'email': item.email,
             'role': item.role} for item in users
        ]})

    def post(self):
        # Создаём нового пользователя
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            login=args['login'],
            hashed_password=args['hashed_password'],
            email=args['email'],
            role=args['role']
        )
        session.add(user)
        session.commit()
        session.close()
        return jsonify({'id': user.id})