from flask import Blueprint, request
from common.bcrypt import bcrypt
from user.models import User
from db import db
import jwt, os
from datetime import datetime, timedelta
from marshmallow import Schema, fields, ValidationError

auth_blp = Blueprint("auth", __name__)

class UserRegistrationSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    bio = fields.String(required=True)

@auth_blp.route("/registration", methods=["POST"])
def register():
    data = request.get_json()
    schema = UserRegistrationSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    if not data['username'] or not data['password'] or not data['bio']:
        return {
            'error_message': 'username, password, and bio cannot be blank'
        }, 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], bio=data['bio'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return{
        'id': new_user.id,
        'username': new_user.username,
        'bio': new_user.bio
    }, 200

@auth_blp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error": "Username or password incorrect"}, 401
    
    valid_password = bcrypt.check_password_hash(user.password, password)
    if not valid_password:
        return {"error": "Username or password incorrect"}, 401
    
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(minutes=20)
    }
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

    return {
        'token': token
    }, 200