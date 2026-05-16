from flask import jsonify, abort
from flask_restful import Resource, reqparse
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
    # Если экскурсия не найдена, возвращаем код ошибки 404
    session = db_session.create_session()
    excursion = session.query(Excursion).get(exc_id)
    if not excursion:
        abort(404)


class ExcursionsResource(Resource):
    def get(self, exc_id):
        # Получаем одну конкретную экскурсию
        abort_if_excursions_not_found(exc_id)
        session = db_session.create_session()
        excursion = session.get(Excursion, exc_id)
        session.close()
        return jsonify({'excursion':
            {'id': excursion.id,
             'title': excursion.title,
             'description': excursion.description,
             'price': excursion.price,
             'way': excursion.way}
        })

    def delete(self, exc_id):
        # Удаляем одну конкретную экскурсию
        abort_if_excursions_not_found(exc_id)
        session = db_session.create_session()
        excursion = session.get(Excursion, exc_id)
        session.delete(excursion)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    def put(self, exc_id):
        # Изменяем одну конкретную экскурсию
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
        session.close()
        return jsonify({'success': 'OK'})


class ExcursionsListResource(Resource):
    def get(self):
        # Получаем список всех экскурсий
        session = db_session.create_session()
        excursions = session.query(Excursion).all()
        session.close()
        return jsonify({'excursions': [
            {'id': item.id,
             'title': item.title,
             'description': item.description,
             'price': item.price,
             'img': item.img,
             'way': item.way,
             'img_way': item.img_way} for item in excursions
        ]})

    def post(self):
        # Создаём новую экскурсию
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
        session.close()
        return jsonify({'id': excursion.id})