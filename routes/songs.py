import os
import time

from flask import Blueprint, current_app, request

from ..models.song_model import (
    create_song,
    delete_song,
    get_all_songs,
    get_song_by_id,
    search_songs,
    update_song as update_song_record,
)
from .common import is_admin
from .response import get_response


songs_bp = Blueprint("songs", __name__)


def save_upload(file_storage, prefix=""):
    filename = f"{prefix}{int(time.time())}_{file_storage.filename}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file_storage.save(upload_path)
    return f"/uploads/{filename}"


@songs_bp.route("/api/songs", methods=["GET"])
def get_all_song():
    try:
        user_id = request.args.get("userId")
        return get_response(get_all_songs(user_id))
    except Exception as error:
        print(error)
        return get_response({"error": "Khong lay duoc danh sach bai hat"}, 500)


@songs_bp.route("/api/songs/search", methods=["GET"])
def search_song():
    try:
        keyword = request.args.get("q", "")
        return get_response(search_songs(keyword))
    except Exception as error:
        print(error)
        return get_response({"error": "Khong tim kiem duoc bai hat"}, 500)


@songs_bp.route("/api/songs", methods=["POST"])
def add_song():
    try:
        if not is_admin(request.headers.get("role")):
            return get_response({"error": "Permission denied"}, 403)

        if "song" not in request.files:
            return get_response({"error": "No song file"}, 400)

        title = request.form.get("title")
        artist = request.form.get("artist")
        song_url = save_upload(request.files["song"])
        image_file = request.files.get("image")
        image_url = save_upload(image_file, "img_") if image_file else None

        create_song(title, artist, song_url, image_url)
        return get_response({"message": "Upload success"})
    except Exception as error:
        print(error)
        return get_response({"error": "Upload that bai"}, 500)


@songs_bp.route("/api/songs/<song_id>", methods=["PUT"])
def update_song(song_id):
    try:
        if not is_admin(request.headers.get("role")):
            return get_response({"error": "Permission denied"}, 403)

        song = get_song_by_id(song_id)
        if not song:
            return get_response({"error": "Not found"}, 404)

        title = request.form.get("title")
        artist = request.form.get("artist")
        song_file = request.files.get("song")
        image_file = request.files.get("image")

        file_url = save_upload(song_file) if song_file else song.fileUrl
        image_url = save_upload(image_file, "img_") if image_file else song.imageUrl

        update_song_record(song_id, title, artist, file_url, image_url)
        return get_response({"message": "Updated"})
    except Exception as error:
        print(error)
        return get_response({"error": "Cap nhat that bai"}, 500)


@songs_bp.route("/api/songs/<song_id>", methods=["DELETE"])
def delete_song_route(song_id):
    try:
        if not is_admin(request.headers.get("role")):
            return get_response({"error": "Permission denied"}, 403)

        song = get_song_by_id(song_id)
        if not song:
            return get_response({"error": "Not found"}, 404)

        for file_url in [song.fileUrl, song.imageUrl]:
            if not file_url:
                continue
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                file_url.replace("/uploads/", ""),
            )
            if os.path.exists(file_path):
                os.remove(file_path)

        delete_song(song_id)
        return get_response({"message": "Deleted"})
    except Exception as error:
        print(error)
        return get_response({"error": "Xoa that bai"}, 500)

