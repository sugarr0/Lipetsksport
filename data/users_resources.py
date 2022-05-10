from flask_restful import reqparse, abort, Api, Resource
from data.db_session import create_session
from data.users import User
from flask import jsonify, request


def abort_if_not_found(users_id):
    session = create_session()
    users = session.query(User).get(users_id)
    if not users:
        abort(404, message=f"Users {users_id} not found")


class UsersResource(Resource):
    def get(self, users_id):
        abort_if_not_found(users_id)
        db_sess = create_session()
        user = db_sess.query(User).filter(User.id == users_id).first()
        return jsonify(
            {
                'users':
                    user.to_dict(only=('name', 'surname', 'age', 'position', 'speciality', 'address', 'city_from'))
            }
        )
    # wgfwrg

    def delete(self, users_id):
        abort_if_not_found(users_id)
        db_sess = create_session()
        user = db_sess.query(User).get(users_id)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('surname', required=True)
parser.add_argument('email', required=True)
parser.add_argument('city', required=True)
parser.add_argument('password', required=True)


class UsersListResource(Resource):
    def get(self):
        db_sess = create_session()
        users = db_sess.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('name', 'surname', 'city'))
                     for item in users]
            }
        )

    def post(self):
        args = parser.parse_args()
        db_sess = create_session()
        user = User(
            name=args['name'],
            email=args['email'],
            surname=args['surname'],
            city=args['city']
        )
        user.set_password(args['password'])
        db_sess.add(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})
