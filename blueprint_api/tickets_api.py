import flask

from data import db_session
from data.tickets import Ticket

from flask import *

blueprint_t = flask.Blueprint(
    'tickets_api',
    __name__,
    template_folder='templates'
)


@blueprint_t.route('/api/gt_tics', methods=['GET'])
def get_all_tickets():
    db_sess = db_session.create_session()
    tickets = db_sess.query(Ticket).all()
    return jsonify([{'id': x.id, 'id_event': x.id_event, 'name_event': x.name_event, 'price_event': x.price_event, \
                     'id_user': x.id_user, 'name_user': x.name_user, 'count_of_people': x.count_of_people} for x in tickets])


@blueprint_t.route('/api/gt_tics/<int:tic_id>', methods=['GET'])
def get_one_ticket(tic_id):
    db_sess = db_session.create_session()
    ticket = db_sess.query(Ticket).filter(Ticket.id == tic_id).first()
    return jsonify({'id': ticket.id, 'id_event': ticket.id_event, 'name_event': ticket.name_event, \
                    'price_event': ticket.price_event, 'id_user': ticket.id_user, 'name_user': ticket.name_user, \
                    'count_of_people': ticket.count_of_people})


@blueprint_t.route('/api/cr_tic', methods=['POST'])
def post_one_ticket():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['id_event', 'name_event', 'price_event', 'id_user', 'name_user', 'count_of_people']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    ticket = Ticket(
        id_event=request.json['id_event'],
        name_event=request.json['name_event'],
        price_event=request.json['price_event'],
        id_user=request.json['id_user'],
        name_user=request.json['name_user'],
        count_of_people=request.json['count_of_people']
    )
    db_sess.add(ticket)
    db_sess.commit()
    return jsonify({'id': ticket.id})


@blueprint_t.route('/api/pt_tic/<int:tic_id>', methods=['PUT'])
def redact_ticket(tic_id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    db_sess = db_session.create_session()
    ticket = db_sess.get(Ticket, tic_id)
    for atr in ['id_event', 'name_event', 'price_event', 'id_user', 'name_user', 'count_of_people']:
        if atr in request.json:
            setattr(ticket, atr, request.json[atr])
    db_sess.commit()
    return jsonify({'id': ticket.id})


@blueprint_t.route('/api/dl_tic/<int:tic_id>', methods=['DELETE'])
def delete_ticket(tic_id):
    db_sess = db_session.create_session()
    ticket = db_sess.get(Ticket, tic_id)
    if not ticket:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(ticket)
    db_sess.commit()
    return jsonify({'success': 'OK'})