from flask import Blueprint, request, jsonify
from auth.utils import decode_jwt
from tweets.models import Tweet, db
from marshmallow import Schema, fields, ValidationError

tweet_blp = Blueprint("tweet", __name__)

class TweetSchema(Schema):
    tweet = fields.String(required=True)

@tweet_blp.route("/", methods=["POST"])
def post_tweet():
    authorization_header = request.headers.get('Authorization')

    token = authorization_header.split("Bearer ")[1] if "Bearer " in authorization_header else None

    payload = decode_jwt(token) 
    print("Decoded Payload:", payload)

    if not payload or 'user_id' not in payload:
        return {"error": "Token tidak valid"}, 401

    user_id = payload['user_id']

    try:
        data = TweetSchema().load(request.get_json())
    except ValidationError as err:
        return {"error": err.messages}, 400

    tweet = data.get("tweet")

    if not tweet or len(tweet) > 150:
        return {"error": "Tweet tidak boleh lebih dari 150 karakter"}, 400

    new_tweet = Tweet(user_id=user_id, tweet=tweet)
    db.session.add(new_tweet)
    db.session.commit()

    return jsonify({
        'id': new_tweet.id,
        'published_at': new_tweet.published_at.isoformat(),
        'tweet': new_tweet.tweet
    }), 200