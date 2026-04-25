from flask import jsonify, abort
from flask_restful import Resource, reqparse
from data.users import User
from data import db_session


def abort_if_users_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        return jsonify({'user': user.to_dict(
            only=('user_id', 'login', 'email', 'role'))})

    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'login', 'email', 'role')) for item in users]})

    def post(self):
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
        return jsonify({'id': user.id})


if __name__ == "__main__":
    parser = reqparse.RequestParser()
    parser.add_argument('login', required=True)
    parser.add_argument('hashed_password', required=True)
    parser.add_argument('email', required=True)
    parser.add_argument('role', required=True)