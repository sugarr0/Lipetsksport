import flask
from flask import jsonify, request

from . import db_session
from .users import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('name', 'surname', 'age', 'position', 'speciality', 'address', 'city_from'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user:
        return jsonify(
            {
                'users':
                    user.to_dict(only=('name', 'surname', 'age', 'position', 'speciality', 'address', 'city_from'))
            }
        )
    return jsonify({'error': 'Not found'})


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'surname', 'email', 'age', 'password']):
        return jsonify({'error': 'Bad request'})

    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.email == request.json['email']).first():
        return jsonify({'error': 'such user already exists'})
    user = User(
        name=request.json['name'],
        email=request.json['email'],
        surname=request.json['surname'],
        age=request.json['age']
    )
    user.set_password(request.json['password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['POST'])
def update_user(user_id):
    u = user_id
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    for key in request.json:
        if key not in ['name', 'surname', 'age', 'email', 'position', 'speciality', 'address', 'city_from',
                       'modified_date', 'password']:
            return jsonify({'error': 'Keys error'})
        if key == 'name':
            user.name = request.json[key]
        elif key == 'surname':
            user.surname = request.json[key]
        elif key == 'age':
            user.age = request.json[key]
        elif key == 'email':
            user.email = request.json[key]
        elif key == 'position':
            user.position = request.json[key]
        elif key == 'speciality':
            user.speciality = request.json[key]
        elif key == 'address':
            user.address = request.json[key]
        elif key == 'city_from':
            user.city_from = request.json[key]
        elif key == 'modified_date':
            user.modified_date = request.json[key]
        elif key == 'password':
            user.set_password(request.json[key])
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})
