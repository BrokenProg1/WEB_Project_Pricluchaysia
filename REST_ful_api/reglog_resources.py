from flask import jsonify, abort
from flask_restful import Resource, reqparse

from data.users import User
from data import db_session


parser = reqparse.RequestParser()
parser.add_argument('login', required=True)
parser.add_argument('password', required=True)
parser.add_argument('email', required=True)


class RegisterResource(Resource):
    def post(self):
        # Регистрируем нового пользователя на сайт
        db_sess = db_session.create_session()
        args = parser.parse_args()
        user = User(
            login=args['login'],
            email=args['email'],
            role='user'
        )
        if db_sess.query(User).filter(User.email == args['email']).first():
            abort(409)
        user.set_password(args['password'])
        db_sess.add(user)
        db_sess.commit()
        session.close()
        return jsonify({'id': user.id})