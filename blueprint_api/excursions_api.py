import flask

from data import db_session
from data.excursions import Excursion

from flask import *


blueprint_e = flask.Blueprint(
    'excursions_api',
    __name__,
    template_folder='templates'
)


@blueprint_e.route('/api/gt_excursions', methods=['GET'])
def get_all_excursions():
    db_sess = db_session.create_session()
    excursions = db_sess.query(Excursion).all()
    return jsonify([{'id': x.id, 'title': x.title, 'description': x.description, 'price': x.price, 'img': x.img} for x in excursions])


@blueprint_e.route('/api/gt_excursions/<int:exc_id>', methods=['GET'])
def get_one_excursion(exc_id):
    db_sess = db_session.create_session()
    excursion = db_sess.query(Excursion).filter(Excursion.id == exc_id).first()
    return jsonify({'id': excursion.id, 'title': excursion.title, 'description': excursion.description, \
                    'price': excursion.price, 'img': excursion.img})


@blueprint_e.route('/api/cr_exc', methods=['POST'])
def post_one_excursion():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['title', 'description', 'price', 'img']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    excursion = Excursion(
        title=request.json['title'],
        description=request.json['description'],
        price=request.json['price'],
        img=request.json['img']
    )
    db_sess.add(excursion)
    db_sess.commit()
    return jsonify({'id': excursion.id})


@blueprint_e.route('/api/pt_exc/<int:exc_id>', methods=['PUT'])
def redact_excursion(exc_id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    db_sess = db_session.create_session()
    excursion = db_sess.get(Excursion, exc_id)
    for atr in ['login', 'email', 'role']:
        if atr in request.json:
            setattr(excursion, atr, request.json[atr])
    db_sess.commit()
    return jsonify({'id': excursion.id})


@blueprint_e.route('/api/dl_exc/<int:exc_id>', methods=['DELETE'])
def delete_excursion(exc_id):
    db_sess = db_session.create_session()
    excursion = db_sess.get(Excursion, exc_id)
    if not excursion:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(excursion)
    db_sess.commit()
    return jsonify({'success': 'OK'})