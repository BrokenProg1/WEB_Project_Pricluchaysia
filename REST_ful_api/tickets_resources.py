from flask import jsonify, abort
from flask_restful import Resource, reqparse
from data.tickets import Ticket
from data import db_session


parser = reqparse.RequestParser()
parser.add_argument('id_event', required=True, type=int)
parser.add_argument('name_event', required=True)
parser.add_argument('price_event', required=True, type=int)
parser.add_argument('id_user', required=True, type=int)
parser.add_argument('name_user', required=True)
parser.add_argument('count_of_people', required=True, type=int)


def abort_if_tickets_not_found(tic_id):
    # Если запись на экскурсию не найдена, возвращаем код ошибки 404
    session = db_session.create_session()
    ticket = session.query(Ticket).get(tic_id)
    if not ticket:
        abort(404)


class TicketsResource(Resource):
    def get(self, tic_id):
        # Получаем одну конкретную запись
        abort_if_tickets_not_found(tic_id)
        session = db_session.create_session()
        ticket = session.get(Ticket, tic_id)
        session.close()
        return jsonify({'ticket':
            {'id': ticket.id,
             'id_event': ticket.id_event,
             'name_event': ticket.name_event,
             'price_event': ticket.price_event,
             'id_user': ticket.id_user,
             'name_user': ticket.name_user,
             'count_of_people': ticket.count_of_people}})

    def delete(self, tic_id):
        # Удаляем одну конкретную запись
        abort_if_tickets_not_found(tic_id)
        session = db_session.create_session()
        ticket = session.get(Ticket, tic_id)
        session.delete(ticket)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class TicketsListResource(Resource):
    def get(self):
        # Получаем список всех записей
        session = db_session.create_session()
        tickets = session.query(Ticket).all()
        session.close()
        return jsonify({'tickets': [
            {'id': item.id,
             'id_event': item.id_event,
             'name_event': item.name_event,
             'price_event': item.price_event,
             'id_user': item.id_user,
             'name_user': item.name_user,
             'count_of_people': item.count_of_people} for item in tickets
        ]})

    def post(self):
        # Создаём объект новой записи
        args = parser.parse_args()
        session = db_session.create_session()
        ticket = Ticket(
            id_event=args['id_event'],
            name_event=args['name_event'],
            price_event=args['price_event'],
            id_user=args['id_user'],
            name_user=args['name_user'],
            count_of_people=args['count_of_people']
        )
        session.add(ticket)
        session.commit()
        session.close()
        return jsonify({'id': ticket.id})