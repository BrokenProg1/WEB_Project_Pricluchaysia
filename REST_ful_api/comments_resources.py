from flask import jsonify, abort
from flask_restful import Resource, reqparse
from data.comments import Comment
from data import db_session

from datetime import datetime


def abort_if_comments_not_found(com_id):
    session = db_session.create_session()
    comment = session.query(Comment).get(com_id)
    if not comment:
        abort(404, message=f"Comment {com_id} not found")


class CommentsResource(Resource):
    def get(self, com_id):
        abort_if_comments_not_found(com_id)
        session = db_session.create_session()
        comment = session.get(Comment, com_id)
        return jsonify({'comment': comment.to_dict(
            only=('id', 'id_event', 'id_user', 'name_user',
                  'role_user', 'text', 'date'))})

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
        return jsonify({'comments': [item.to_dict(
            only=('id', 'id_event', 'id_user', 'name_user',
                  'role_user', 'text', 'date')) \
            for item in comments]})

    def post(self):
        args = parser.parse_args()
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


if __name__ == "__main__":
    parser = reqparse.RequestParser()
    parser.add_argument('id_event', required=True, type=int)
    parser.add_argument('id_user', required=True, type=int)
    parser.add_argument('name_user', required=True)
    parser.add_argument('role_user', required=True)
    parser.add_argument('text', required=True)
    parser.add_argument('date', required=True, type=datetime)