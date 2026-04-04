from flask import Blueprint, request

from models.playlist_model import (
    add_song_to_playlist,
    create_playlist,
    fetch_playlist_songs,
    fetch_playlists,
    get_playlist_for_user,
    get_playlist_song,
)
from routes.response import get_response


playlists_bp = Blueprint("playlists", __name__)


@playlists_bp.route("/api/playlists", methods=["GET"])
def get_all_playlist():
    try:
        user_id = request.args.get("userId")
        return get_response(fetch_playlists(user_id))
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong lay duoc playlist"}, 500)


@playlists_bp.route("/api/playlists", methods=["POST"])
def add_playlist():
    try:
        user_id = request.json.get("userId")
        name = (request.json.get("name") or "").strip()

        if not user_id or not name:
            return get_response({"error": "Missing playlist data"}, 400)

        playlist = create_playlist(user_id, name)
        return get_response(
            {
                "message": "Playlist created",
                "playlist": {
                    "id": playlist.id,
                    "name": playlist.name,
                    "songCount": 0,
                },
            }
        )
    except Exception as exc:
        print(exc)
        return get_response({"error": "Tao playlist that bai"}, 500)


@playlists_bp.route("/api/playlists/<playlist_id>/songs", methods=["GET"])
def get_song_by_playlist(playlist_id):
    try:
        user_id = request.args.get("userId")
        if not get_playlist_for_user(playlist_id, user_id):
            return get_response({"error": "Playlist not found"}, 404)

        return get_response(fetch_playlist_songs(playlist_id, user_id))
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong lay duoc bai hat trong playlist"}, 500)


@playlists_bp.route("/api/playlists/<playlist_id>/songs", methods=["POST"])
def create_song_in_playlist(playlist_id):
    try:
        user_id = request.json.get("userId")
        song_id = request.json.get("songId")

        if not get_playlist_for_user(playlist_id, user_id):
            return get_response({"error": "Playlist not found"}, 404)

        if get_playlist_song(playlist_id, song_id):
            return get_response({"message": "Song already in playlist"})

        add_song_to_playlist(playlist_id, song_id)
        return get_response({"message": "Song added to playlist"})
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong them duoc bai hat vao playlist"}, 500)
