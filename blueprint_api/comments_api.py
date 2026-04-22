import flask

from data import db_session
from data.comments import Comment

from flask import *

blueprint_c = flask.Blueprint(
    'comments_api',
    __name__,
    template_folder='templates'
)


@blueprint_c.route('/api/gt_coms', methods=['GET'])
def get_all_comments():
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).all()
    return jsonify([{'id': x.id, 'id_event': x.id_event, 'id_user': x.id_user, 'name_user': x.name_user, \
                     'role_user': x.role_user, 'text': x.text, 'date': x.date} for x in comments])


@blueprint_c.route('/api/gt_coms/<int:com_id>', methods=['GET'])
def get_one_comment(com_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == com_id).first()
    return jsonify({'id': comment.id, 'id_event': comment.id_event, 'id_user': comment.id_user, \
                    'name_user': comment.name_user, 'role_user': comment.role_user, 'text': comment.text, 'date': comment.date})


@blueprint_c.route('/api/cr_com', methods=['POST'])
def post_one_comment():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['id_event', 'id_user', 'name_user', 'role_user', 'text', 'date']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    comment = Comment(
        id_event=request.json['id_event'],
        id_user=request.json['id_user'],
        name_user=request.json['name_user'],
        role_user=request.json['role_user'],
        text=request.json['text'],
        date=request.json['date']
    )
    db_sess.add(comment)
    db_sess.commit()
    return jsonify({'id': comment.id})


@blueprint_c.route('/api/pt_com/<int:com_id>', methods=['PUT'])
def redact_comment(com_id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    db_sess = db_session.create_session()
    comment = db_sess.get(Comment, com_id)
    for atr in ['id_event', 'name_event', 'price_event', 'id_user', 'name_user', 'count_of_people']:
        if atr in request.json:
            setattr(comment, atr, request.json[atr])
    db_sess.commit()
    return jsonify({'id': comment.id})


@blueprint_c.route('/api/dl_com/<int:com_id>', methods=['DELETE'])
def delete_comment(com_id):
    db_sess = db_session.create_session()
    comment = db_sess.get(Comment, com_id)
    if not comment:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(comment)
    db_sess.commit()
    return jsonify({'success': 'OK'})