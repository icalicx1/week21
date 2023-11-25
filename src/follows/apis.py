from flask import Blueprint, request
from user.models import User, db 
from auth.utils import decode_jwt

follow_blp = Blueprint("follow", __name__)

# following a user
@follow_blp.route("/<int:user_id>", methods=["POST"])
def follow_user(user_id):
    authorization_header = request.headers.get('Authorization')

    if not authorization_header:
        return {"error": "Authorization header is missing"}, 401

    token = authorization_header.split("Bearer ")[1] if "Bearer " in authorization_header else None

    if not token:
        return {"error": "Invalid token format"}, 401

    payload = decode_jwt(token) 
    print("Decoded Payload:", payload)

    if not payload:
        return {"error": "Token tidak valid"}, 401

    current_user_id = payload.get("user_id")

    if not current_user_id:
        return {"error": "User ID not found in token"}, 401

    current_user = User.query.get(current_user_id)
    user_to_follow = User.query.get(user_id)

    if not current_user or not user_to_follow:
        return {"error": "User not found!"}, 404
    
    if current_user_id == user_id:
        return {"error": "tidak bisa follow diri sendiri"}, 400

    if current_user.follow(user_to_follow):
        db.session.commit()
        return {"message": f"You are now following {user_to_follow.username}"}

    return {"message": "You are already following this user"}

# unfollowing a user
@follow_blp.route("/unfollow/<int:user_id>", methods=["POST"])
def unfollow_user(user_id):
    authorization_header = request.headers.get('Authorization')

    if not authorization_header:
        return {"error": "Authorization header is missing"}, 401

    token = authorization_header.split("Bearer ")[1] if "Bearer " in authorization_header else None

    if not token:
        return {"error": "Invalid token format"}, 401

    payload = decode_jwt(token) 
    print("Decoded Payload:", payload)

    if not payload:
        return {"error": "Token tidak valid"}, 401

    current_user_id = payload.get("user_id")

    if not current_user_id:
        return {"error": "User ID not found in token"}, 401

    current_user = User.query.get(current_user_id)
    user_to_unfollow = User.query.get(user_id)

    if not current_user or not user_to_unfollow:
        return {"error": "User not found!"}, 404
    
    if current_user_id == user_id:
        return {"error": "You are not following yourself"}, 400

    if current_user.unfollow(user_to_unfollow):
        db.session.commit()
        return {"message": f"You have unfollowed {user_to_unfollow.username}"}

    return {"message": "You were not following this user"}