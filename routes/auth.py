from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash

from models.user_model import create_user, get_user_by_username
from routes.response import get_response


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    try:
        username = request.json.get("username")
        password = request.json.get("password")

        if not username or not password:
            return get_response({"error": "Missing data"}, 400)

        create_user(username, generate_password_hash(password))
        return get_response({"message": "Register success"})
    except Exception as exc:
        print(exc)
        return get_response({"error": "Username exists"}, 400)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        user = get_user_by_username(username)

        if user and check_password_hash(user.password, password):
            return get_response(
                {
                    "message": "Login success",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "role": user.role,
                    },
                }
            )

        return get_response({"error": "Invalid login"}, 401)
    except Exception as exc:
        print(exc)
        return get_response({"error": "Dang nhap that bai"}, 500)
