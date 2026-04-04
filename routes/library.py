from flask import Blueprint, request

from models.library_model import (
    add_favorite,
    add_recent_song,
    fetch_favorites_by_user,
    fetch_recent_songs,
    get_favorite,
    remove_favorite,
)
from routes.response import get_response


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
    except Exception as exc:
        print(exc)
        return get_response({"error": "Them yeu thich that bai"}, 500)


@library_bp.route("/api/favorites", methods=["DELETE"])
def delete_favorite():
    try:
        user_id = request.json.get("userId")
        song_id = request.json.get("songId")
        remove_favorite(user_id, song_id)
        return get_response({"message": "Removed"})
    except Exception as exc:
        print(exc)
        return get_response({"error": "Xoa yeu thich that bai"}, 500)


@library_bp.route("/api/favorites/<id>", methods=["GET"])
def get_favorite_by_user(id):
    try:
        return get_response(fetch_favorites_by_user(id))
    except Exception as exc:
        print(exc)
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
    except Exception as exc:
        print(exc)
        return get_response({"error": "Cap nhat yeu thich that bai"}, 500)


@library_bp.route("/api/recent", methods=["POST"])
def add_recent():
    try:
        user_id = request.json.get("userId")
        song_id = request.json.get("songId")
        add_recent_song(user_id, song_id)
        return get_response({"message": "Added recent"})
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong them duoc recent"}, 500)


@library_bp.route("/api/recent/<id>", methods=["GET"])
def get_recent(id):
    try:
        return get_response(fetch_recent_songs(id))
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong lay duoc recent"}, 500)
