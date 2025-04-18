import os
import secrets
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
db = SQLAlchemy(app)
api = Api(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


with app.app_context():
    db.create_all()


class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if user:
                return jsonify({'id': user.id, 'name': user.name, 'email': user.email})
            return {'message': 'User not found'}, 404
        users = User.query.all()
        return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])

    def post(self):
        data = request.get_json()
        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created'}, 201

    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        data = request.get_json()
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        db.session.commit()
        return {'message': 'User updated successfully'}

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}


api.add_resource(UserResource, '/users', '/users/<int:user_id>')


@app.route('/')
def home():
    return "Welcome to My Internship Flask API!"


print(f"Generated SECRET_KEY: {app.config['SECRET_KEY']}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
