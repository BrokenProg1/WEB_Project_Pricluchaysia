from flask import jsonify, abort
from flask_restful import Resource, reqparse
from data.excursions import Excursion
from data import db_session


def abort_if_excursions_not_found(exc_id):
    session = db_session.create_session()
    excursion = session.query(Excursion).get(exc_id)
    if not excursion:
        abort(404, message=f"Excursion {exc_id} not found")


class ExcursionsResource(Resource):
    def get(self, exc_id):
        abort_if_excursions_not_found(exc_id)
        session = db_session.create_session()
        excursion = session.get(Excursion, exc_id)
        return jsonify({'excursion': excursion.to_dict(
            only=('id', 'title', 'description', 'price'))})

    def delete(self, exc_id):
        abort_if_excursions_not_found(exc_id)
        session = db_session.create_session()
        excursion = session.get(Excursion, exc_id)
        session.delete(excursion)
        session.commit()
        return jsonify({'success': 'OK'})


class ExcursionsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        excursions = session.query(Excursion).all()
        return jsonify({'excursions': [item.to_dict(
            only=('id', 'title', 'description', 'price')) for item in excursions]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        excursion = Excursion(
            title=args['title'],
            description=args['description'],
            price=args['price'],
            img=args['img']
        )
        session.add(excursion)
        session.commit()
        return jsonify({'id': excursion.id})


if __name__ == "__main__":
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)
    parser.add_argument('description', required=True)
    parser.add_argument('price', required=True, type=int)
    parser.add_argument('img', required=True, type=str)