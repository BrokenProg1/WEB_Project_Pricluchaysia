from flask import jsonify, abort
from flask_restful import Resource, reqparse
from data.tickets import Ticket
from data import db_session


def abort_if_tickets_not_found(tic_id):
    session = db_session.create_session()
    ticket = session.query(Ticket).get(tic_id)
    if not ticket:
        abort(404, message=f"Ticket {tic_id} not found")


class TicketsResource(Resource):
    def get(self, tic_id):
        abort_if_tickets_not_found(tic_id)
        session = db_session.create_session()
        ticket = session.get(Ticket, tic_id)
        return jsonify({'ticket': ticket.to_dict(
            only=('id', 'id_event', 'name_event', 'price_event',
                  'id_user', 'name_user', 'count_of_people'))})

    def delete(self, tic_id):
        abort_if_tickets_not_found(tic_id)
        session = db_session.create_session()
        ticket = session.get(Ticket, tic_id)
        session.delete(ticket)
        session.commit()
        return jsonify({'success': 'OK'})


class TicketsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tickets = session.query(Ticket).all()
        return jsonify({'tickets': [item.to_dict(
            only=('id', 'id_event', 'name_event', 'price_event',
                  'id_user', 'name_user', 'count_of_people')) \
            for item in tickets]})

    def post(self):
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
        return jsonify({'id': ticket.id})


if __name__ == "__main__":
    parser = reqparse.RequestParser()
    parser.add_argument('id_event', required=True, type=int)
    parser.add_argument('name_event', required=True)
    parser.add_argument('price_event', required=True, type=int)
    parser.add_argument('id_user', required=True, type=int)
    parser.add_argument('name_user', required=True)
    parser.add_argument('count_of_people', required=True, type=int)