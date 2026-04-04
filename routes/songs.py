from flask import Blueprint, current_app, request, send_from_directory

from models.song_model import (
    delete_song_relations,
    fetch_song_for_download,
    fetch_all_songs,
    get_song_by_id,
    insert_song,
    search_songs,
    update_song,
)
from routes.common import build_download_name, is_admin, remove_uploaded_file, save_uploaded_file
from routes.response import get_response


songs_bp = Blueprint("songs", __name__)


@songs_bp.route("/api/songs", methods=["GET"])
def get_all_song():
    try:
        user_id = request.args.get("userId")
        return get_response(fetch_all_songs(user_id))
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong lay duoc danh sach bai hat"}, 500)


@songs_bp.route("/api/songs/search", methods=["GET"])
def search_song():
    try:
        query = request.args.get("q", "")
        return get_response(search_songs(query))
    except Exception as exc:
        print(exc)
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
        song_file = request.files["song"]
        image_file = request.files.get("image")

        file_url = save_uploaded_file(song_file)
        image_url = save_uploaded_file(image_file, "img_") if image_file else None

        insert_song(title, artist, file_url, image_url)
        return get_response({"message": "Upload success"})
    except Exception as exc:
        print(exc)
        return get_response({"error": "Upload that bai"}, 500)


@songs_bp.route("/api/songs/<id>", methods=["PUT"])
def edit_song(id):
    try:
        if not is_admin(request.headers.get("role")):
            return get_response({"error": "Permission denied"}, 403)

        song = get_song_by_id(id)
        if not song:
            return get_response({"error": "Not found"}, 404)

        title = request.form.get("title")
        artist = request.form.get("artist")
        song_file = request.files.get("song")
        image_file = request.files.get("image")

        file_url = song.fileUrl
        image_url = song.imageUrl

        if song_file:
            remove_uploaded_file(file_url)
            file_url = save_uploaded_file(song_file)

        if image_file:
            remove_uploaded_file(image_url)
            image_url = save_uploaded_file(image_file, "img_")

        update_song(id, title, artist, file_url, image_url)
        return get_response({"message": "Updated"})
    except Exception as exc:
        print(exc)
        return get_response({"error": "Cap nhat that bai"}, 500)


@songs_bp.route("/api/songs/<id>", methods=["DELETE"])
def delete_song(id):
    try:
        if not is_admin(request.headers.get("role")):
            return get_response({"error": "Permission denied"}, 403)

        song = get_song_by_id(id)
        if not song:
            return get_response({"error": "Not found"}, 404)

        remove_uploaded_file(song.fileUrl)
        remove_uploaded_file(song.imageUrl)
        delete_song_relations(id)
        return get_response({"message": "Deleted"})
    except Exception as exc:
        print(exc)
        return get_response({"error": "Xoa that bai"}, 500)


@songs_bp.route("/api/songs/<id>/download", methods=["GET"])
def download_song(id):
    try:
        song = fetch_song_for_download(id)
        if not song or not song.fileUrl:
            return get_response({"error": "Song not found"}, 404)

        stored_filename = song.fileUrl.replace("/uploads/", "", 1)
        return send_from_directory(
            current_app.config["UPLOAD_FOLDER"],
            stored_filename,
            as_attachment=True,
            download_name=build_download_name(song),
        )
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong tai duoc bai hat"}, 500)
