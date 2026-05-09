from flask import jsonify, abort, Flask
from flask_restful import Resource, reqparse, Api
from data.excursions import Excursion
from data import db_session


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('description', required=True)
parser.add_argument('price', required=True, type=int)
parser.add_argument('img', required=True, type=str)
parser.add_argument('way', required=True, type=str)
parser.add_argument('img_way', required=True, type=str)


def abort_if_excursions_not_found(exc_id):
    session = db_session.create_session()
    excursion = session.query(Excursion).get(exc_id)
    if not excursion:
        abort(404)


class ExcursionsResource(Resource):
    def get(self, exc_id):
        abort_if_excursions_not_found(exc_id)
        session = db_session.create_session()
        excursion = session.get(Excursion, exc_id)
        return jsonify({'excursion':
            {'id': excursion.id,
             'title': excursion.title,
             'description': excursion.description,
             'price': excursion.price,
             'way': excursion.way}
        })

    def delete(self, exc_id):
        abort_if_excursions_not_found(exc_id)
        session = db_session.create_session()
        excursion = session.get(Excursion, exc_id)
        session.delete(excursion)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, exc_id):
        abort_if_excursions_not_found(exc_id)
        session = db_session.create_session()
        excursion = session.get(Excursion, exc_id)
        args = parser.parse_args()
        excursion.title = args['title']
        excursion.description = args['description']
        excursion.price = args['price']
        excursion.img = args['img']
        excursion.way = args['way']
        excursion.img_way = args['img_way']
        session.commit()
        return jsonify({'success': 'OK'})


class ExcursionsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        excursions = session.query(Excursion).all()
        return jsonify({'excursions': [
            {'id': item.id,
             'title': item.title,
             'description': item.description,
             'price': item.price,
             'way': item.way} for item in excursions
        ]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        excursion = Excursion(
            title=args['title'],
            description=args['description'],
            price=args['price'],
            img=args['img'],
            way=args['way'],
            img_way=args['img_way']
        )
        session.add(excursion)
        session.commit()
        return jsonify({'id': excursion.id})