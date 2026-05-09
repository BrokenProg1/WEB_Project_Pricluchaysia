from flask import jsonify, abort
from flask_restful import Resource, reqparse
from data.comments import Comment
from data import db_session

from datetime import datetime


parser = reqparse.RequestParser()
parser.add_argument('id_event', required=True, type=int)
parser.add_argument('id_user', required=True, type=int)
parser.add_argument('name_user', required=True)
parser.add_argument('role_user', required=True)
parser.add_argument('text', required=True)
parser.add_argument('date', required=True, type=str)


def abort_if_comments_not_found(com_id):
    session = db_session.create_session()
    comment = session.query(Comment).get(com_id)
    if not comment:
        abort(404)


class CommentsResource(Resource):
    def get(self, com_id):
        abort_if_comments_not_found(com_id)
        session = db_session.create_session()
        comment = session.get(Comment, com_id)
        return jsonify({'comments':
            {'id': comment.id,
             'id_event': comment.id_event,
             'id_user': comment.id_user,
             'name_user': comment.name_user,
             'role_user': comment.role_user,
             'text': comment.text,
             'date': comment.date}})

    def delete(self, com_id):
        abort_if_comments_not_found(com_id)
        session = db_session.create_session()
        ticket = session.get(Comment, com_id)
        session.delete(ticket)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comment).all()
        return jsonify({'comments': [
            {'id': item.id,
             'id_event': item.id_event,
             'id_user': item.id_user,
             'name_user': item.name_user,
             'role_user': item.role_user,
             'text': item.text,
             'date': item.date} for item in comments
        ]})

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        comment = Comment(
            id_event=args['id_event'],
            id_user=args['id_user'],
            name_user=args['name_user'],
            role_user=args['role_user'],
            text=args['text'],
            date=args['date']
        )
        session.add(comment)
        session.commit()
        return jsonify({'id': comment.id})