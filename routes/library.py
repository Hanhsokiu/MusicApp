from flask import Blueprint, request

from ..models.library_model import (
    add_favorite,
    add_recent,
    get_favorite,
    get_favorites_by_user,
    get_recent_by_user,
    remove_favorite,
)
from .response import get_response


library_bp = Blueprint("library", __name__)


@library_bp.route("/api/favorites", methods=["POST"])
def create_favorite():
    try:
        user_id = request.json.get("userId")
        song_id = request.json.get("songId")

        if get_favorite(user_id, song_id):
            return get_response({"message": "Already liked"})

        add_favorite(user_id, song_id)
        return get_response({"message": "Added"})
    except Exception as error:
        print(error)
        return get_response({"error": "Them yeu thich that bai"}, 500)


@library_bp.route("/api/favorites", methods=["DELETE"])
def delete_favorite():
    try:
        user_id = request.json.get("userId")
        song_id = request.json.get("songId")
        remove_favorite(user_id, song_id)
        return get_response({"message": "Removed"})
    except Exception as error:
        print(error)
        return get_response({"error": "Xoa yeu thich that bai"}, 500)


@library_bp.route("/api/favorites/<user_id>", methods=["GET"])
def get_favorite_by_user(user_id):
    try:
        return get_response(get_favorites_by_user(user_id))
    except Exception as error:
        print(error)
        return get_response({"error": "Khong lay duoc danh sach yeu thich"}, 500)


@library_bp.route("/api/favorites/toggle", methods=["POST"])
def toggle_favorite():
    try:
        user_id = request.json.get("userId")
        song_id = request.json.get("songId")

        if get_favorite(user_id, song_id):
            remove_favorite(user_id, song_id)
            return get_response({"status": "removed"})

        add_favorite(user_id, song_id)
        return get_response({"status": "added"})
    except Exception as error:
        print(error)
        return get_response({"error": "Cap nhat yeu thich that bai"}, 500)


@library_bp.route("/api/recent", methods=["POST"])
def create_recent():
    try:
        user_id = request.json.get("userId")
        song_id = request.json.get("songId")
        add_recent(user_id, song_id)
        return get_response({"message": "Added recent"})
    except Exception as error:
        print(error)
        return get_response({"error": "Khong them duoc recent"}, 500)


@library_bp.route("/api/recent/<user_id>", methods=["GET"])
def get_recent(user_id):
    try:
        return get_response(get_recent_by_user(user_id))
    except Exception as error:
        print(error)
        return get_response({"error": "Khong lay duoc recent"}, 500)

