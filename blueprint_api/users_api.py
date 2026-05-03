import flask

from data import db_session
from data.users import User

from flask import *


blueprint_u = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint_u.route('/api/gt_users', methods=['GET'])
def get_all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify([{'id': x.id, 'login': x.login, 'email': x.email, 'role': x.role} for x in users])


@blueprint_u.route('/api/gt_users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return jsonify({'id': user.id, 'login': user.login, 'email': user.email, 'role': user.role})


@blueprint_u.route('/api/cr_user', methods=['POST'])
def post_one_user():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['login', 'hashed_password', 'email', 'role']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    user = User(
        login=request.json['login'],
        hashed_password=request.json['hashed_password'],
        email=request.json['email'],
        role=request.json['role']
    )
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'id': user.id})


@blueprint_u.route('/api/pt_user/<int:user_id>', methods=['PUT'])
def redact_user(user_id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    for atr in ['login', 'email', 'role']:
        if atr in request.json:
            setattr(user, atr, request.json[atr])
    db_sess.commit()
    return jsonify({'id': user.id})


@blueprint_u.route('/api/dl_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})