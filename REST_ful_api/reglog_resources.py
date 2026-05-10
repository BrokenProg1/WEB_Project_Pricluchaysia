from flask import jsonify, abort
from flask_login import login_user, current_user
from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash

from data.users import User
from data import db_session


parser = reqparse.RequestParser()
parser.add_argument('login', required=True)
parser.add_argument('password', required=True)
parser.add_argument('email', required=True)


class RegisterResource(Resource):
    def post(self):
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
        return jsonify({'id': user.id})


"""class LoginResource(Resource):  # Попытка вживления провалилась
    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        user = db_sess.query(User).filter(User.email == args['email']).first()
        if user is None:
            abort(404)
        if not check_password_hash(user.hashed_password, args['password']):
            abort(405)
        login_user(user)"""