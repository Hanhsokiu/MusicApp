from functools import wraps
import os
import time

import pyodbc
from flask import Flask, jsonify, render_template, request, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-IMDB0IM\\SQLEXPRESS;"
    "DATABASE=MusicApp_test;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "music-app-api-secret-key")
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123")


def get_user_by_id(user_id):
    cursor.execute("SELECT id, username, password, role FROM Users WHERE id = ?", (user_id,))
    return cursor.fetchone()


def get_user_by_username(username):
    cursor.execute("SELECT id, username, password, role FROM Users WHERE username = ?", (username,))
    return cursor.fetchone()


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Please login first"}), 401
        return view_func(current_user, *args, **kwargs)

    return wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Please login first"}), 401
        if current_user.role != "admin":
            return jsonify({"error": "Permission denied"}), 403
        return view_func(current_user, *args, **kwargs)

    return wrapped_view


def ensure_default_admin():
    cursor.execute("SELECT TOP 1 id FROM Users WHERE role = ?", ("admin",))
    admin = cursor.fetchone()
    if admin:
        return

    cursor.execute(
        "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
        (DEFAULT_ADMIN_USERNAME, generate_password_hash(DEFAULT_ADMIN_PASSWORD), "admin"),
    )
    conn.commit()


ensure_default_admin()


@app.route("/api/songs", methods=["GET"])
def get_songs():
    current_user = get_current_user()
    user_id = current_user.id if current_user else None

    cursor.execute(
        """
        SELECT s.*,
               CASE WHEN f.songId IS NOT NULL THEN 1 ELSE 0 END AS isFavorite
        FROM Songs s
        LEFT JOIN Favorites f
            ON s.id = f.songId AND f.userId = ?
        """,
        (user_id,),
    )

    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append(
            {
                "id": row.id,
                "title": row.title,
                "artist": row.artist,
                "fileUrl": row.fileUrl,
                "imageUrl": row.imageUrl,
                "isFavorite": row.isFavorite,
            }
        )

    return jsonify(data)


@app.route("/api/songs", methods=["POST"])
@admin_required
def upload_song(current_user):
    if "song" not in request.files:
        return jsonify({"error": "No song file"}), 400

    song_file = request.files["song"]
    image_file = request.files.get("image")
    title = (request.form.get("title") or "").strip()
    artist = (request.form.get("artist") or "").strip()

    if not title or not artist:
        return jsonify({"error": "Missing song information"}), 400

    song_filename = f"{int(time.time())}_{secure_filename(song_file.filename)}"
    song_path = os.path.join(UPLOAD_FOLDER, song_filename)
    song_file.save(song_path)
    file_url = f"/uploads/{song_filename}"

    image_url = None
    if image_file:
        image_filename = f"img_{int(time.time())}_{secure_filename(image_file.filename)}"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image_file.save(image_path)
        image_url = f"/uploads/{image_filename}"

    cursor.execute(
        "INSERT INTO Songs (title, artist, fileUrl, imageUrl) VALUES (?, ?, ?, ?)",
        (title, artist, file_url, image_url),
    )
    conn.commit()

    return jsonify({"message": "Upload success"})


@app.route("/api/songs/search")
def search_song():
    q = request.args.get("q", "").strip()

    cursor.execute("SELECT * FROM Songs WHERE title LIKE ?", ("%" + q + "%",))
    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append(
            {
                "id": row.id,
                "title": row.title,
                "artist": row.artist,
                "fileUrl": row.fileUrl,
                "imageUrl": row.imageUrl,
            }
        )

    return jsonify(data)


@app.route("/api/songs/<int:song_id>", methods=["DELETE"])
@admin_required
def delete_song(current_user, song_id):
    cursor.execute("SELECT fileUrl, imageUrl FROM Songs WHERE id = ?", (song_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Not found"}), 404

    if row.fileUrl:
        path = os.path.join(UPLOAD_FOLDER, row.fileUrl.replace("/uploads/", ""))
        if os.path.exists(path):
            os.remove(path)

    if row.imageUrl:
        path = os.path.join(UPLOAD_FOLDER, row.imageUrl.replace("/uploads/", ""))
        if os.path.exists(path):
            os.remove(path)

    cursor.execute("DELETE FROM Songs WHERE id = ?", (song_id,))
    conn.commit()

    return jsonify({"message": "Deleted"})


@app.route("/api/songs/<int:song_id>", methods=["PUT"])
@admin_required
def update_song(current_user, song_id):
    cursor.execute("SELECT * FROM Songs WHERE id = ?", (song_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Not found"}), 404

    title = (request.form.get("title") or row.title).strip()
    artist = (request.form.get("artist") or row.artist).strip()
    song_file = request.files.get("song")
    image_file = request.files.get("image")

    file_url = row.fileUrl
    image_url = row.imageUrl

    if song_file:
        song_filename = f"{int(time.time())}_{secure_filename(song_file.filename)}"
        song_path = os.path.join(UPLOAD_FOLDER, song_filename)
        song_file.save(song_path)
        file_url = f"/uploads/{song_filename}"

    if image_file:
        image_filename = f"img_{int(time.time())}_{secure_filename(image_file.filename)}"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image_file.save(image_path)
        image_url = f"/uploads/{image_filename}"

    cursor.execute(
        """
        UPDATE Songs
        SET title = ?, artist = ?, fileUrl = ?, imageUrl = ?
        WHERE id = ?
        """,
        (title, artist, file_url, image_url, song_id),
    )
    conn.commit()

    return jsonify({"message": "Updated"})


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Missing data"}), 400

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, "user"),
        )
        conn.commit()
        return jsonify({"message": "Register success"})
    except pyodbc.IntegrityError:
        return jsonify({"error": "Username exists"}), 400


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Missing data"}), 400

    user = get_user_by_username(username)

    if user and check_password_hash(user.password, password):
        session.clear()
        session["user_id"] = user.id
        return jsonify(
            {
                "message": "Login success",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
            }
        )

    return jsonify({"error": "Invalid login"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout success"})


@app.route("/api/me", methods=["GET"])
@login_required
def get_me(current_user):
    return jsonify(
        {
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role,
            }
        }
    )


@app.route("/api/favorites", methods=["POST"])
@login_required
def add_favorite(current_user):
    data = request.get_json(silent=True) or {}
    song_id = data.get("songId")

    cursor.execute(
        "SELECT 1 FROM Favorites WHERE userId = ? AND songId = ?",
        (current_user.id, song_id),
    )
    exists = cursor.fetchone()

    if exists:
        return jsonify({"message": "Already liked"})

    cursor.execute(
        "INSERT INTO Favorites (userId, songId) VALUES (?, ?)",
        (current_user.id, song_id),
    )
    conn.commit()

    return jsonify({"message": "Added"})


@app.route("/api/favorites", methods=["DELETE"])
@login_required
def remove_favorite(current_user):
    data = request.get_json(silent=True) or {}
    song_id = data.get("songId")

    cursor.execute(
        "DELETE FROM Favorites WHERE userId = ? AND songId = ?",
        (current_user.id, song_id),
    )
    conn.commit()

    return jsonify({"message": "Removed"})


@app.route("/api/favorites/<int:user_id>")
@login_required
def get_favorites(current_user, user_id):
    if current_user.role != "admin" and current_user.id != user_id:
        return jsonify({"error": "Permission denied"}), 403

    cursor.execute(
        """
        SELECT s.* FROM Songs s
        JOIN Favorites f ON s.id = f.songId
        WHERE f.userId = ?
        """,
        (user_id,),
    )

    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append(
            {
                "id": row.id,
                "title": row.title,
                "artist": row.artist,
                "fileUrl": row.fileUrl,
                "imageUrl": row.imageUrl,
                "isFavorite": 1,
            }
        )

    return jsonify(data)


@app.route("/api/recent", methods=["POST"])
@login_required
def add_recent(current_user):
    data = request.get_json(silent=True) or {}
    song_id = data.get("songId")

    cursor.execute(
        "INSERT INTO Recent (userId, songId) VALUES (?, ?)",
        (current_user.id, song_id),
    )
    conn.commit()

    return jsonify({"message": "Added recent"})


@app.route("/api/recent/<int:user_id>")
@login_required
def get_recent(current_user, user_id):
    if current_user.role != "admin" and current_user.id != user_id:
        return jsonify({"error": "Permission denied"}), 403

    cursor.execute(
        """
        SELECT TOP 10 s.* FROM Songs s
        JOIN Recent r ON s.id = r.songId
        WHERE r.userId = ?
        ORDER BY r.playedAt DESC
        """,
        (user_id,),
    )

    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append(
            {
                "id": row.id,
                "title": row.title,
                "artist": row.artist,
                "fileUrl": row.fileUrl,
                "imageUrl": row.imageUrl,
            }
        )

    return jsonify(data)


@app.route("/api/favorites/toggle", methods=["POST"])
@login_required
def toggle_favorite(current_user):
    data = request.get_json(silent=True) or {}
    song_id = data.get("songId")

    cursor.execute(
        "SELECT 1 FROM Favorites WHERE userId = ? AND songId = ?",
        (current_user.id, song_id),
    )
    exists = cursor.fetchone()

    if exists:
        cursor.execute(
            "DELETE FROM Favorites WHERE userId = ? AND songId = ?",
            (current_user.id, song_id),
        )
        conn.commit()
        return jsonify({"status": "removed"})

    cursor.execute(
        "INSERT INTO Favorites (userId, songId) VALUES (?, ?)",
        (current_user.id, song_id),
    )
    conn.commit()
    return jsonify({"status": "added"})


@app.route("/api/playlists", methods=["GET"])
@login_required
def get_playlists(current_user):
    cursor.execute(
        """
        SELECT p.id, p.name, COUNT(ps.songId) AS songCount
        FROM Playlists p
        LEFT JOIN PlaylistSongs ps ON p.id = ps.playlistId
        WHERE p.userId = ?
        GROUP BY p.id, p.name
        ORDER BY p.id DESC
        """,
        (current_user.id,),
    )

    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append({"id": row.id, "name": row.name, "songCount": row.songCount})

    return jsonify(data)


@app.route("/api/playlists", methods=["POST"])
@login_required
def create_playlist(current_user):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Playlist name is required"}), 400

    cursor.execute(
        "INSERT INTO Playlists (userId, name) OUTPUT INSERTED.id VALUES (?, ?)",
        (current_user.id, name),
    )
    playlist_id = cursor.fetchone()[0]
    conn.commit()

    return jsonify({"message": "Playlist created", "playlistId": playlist_id}), 201


@app.route("/api/playlists/<int:playlist_id>", methods=["GET"])
@login_required
def get_playlist_songs(current_user, playlist_id):
    cursor.execute(
        "SELECT id, name, userId FROM Playlists WHERE id = ?",
        (playlist_id,),
    )
    playlist = cursor.fetchone()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    if playlist.userId != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Permission denied"}), 403

    cursor.execute(
        """
        SELECT s.*,
               CASE WHEN f.songId IS NOT NULL THEN 1 ELSE 0 END AS isFavorite
        FROM PlaylistSongs ps
        JOIN Songs s ON s.id = ps.songId
        LEFT JOIN Favorites f ON s.id = f.songId AND f.userId = ?
        WHERE ps.playlistId = ?
        ORDER BY ps.id DESC
        """,
        (current_user.id, playlist_id),
    )

    rows = cursor.fetchall()
    songs = []
    for row in rows:
        songs.append(
            {
                "id": row.id,
                "title": row.title,
                "artist": row.artist,
                "fileUrl": row.fileUrl,
                "imageUrl": row.imageUrl,
                "isFavorite": row.isFavorite,
            }
        )

    return jsonify(
        {
            "playlist": {"id": playlist.id, "name": playlist.name},
            "songs": songs,
        }
    )


@app.route("/api/playlists/<int:playlist_id>/songs", methods=["POST"])
@login_required
def add_song_to_playlist(current_user, playlist_id):
    data = request.get_json(silent=True) or {}
    song_id = data.get("songId")

    cursor.execute(
        "SELECT id, userId FROM Playlists WHERE id = ?",
        (playlist_id,),
    )
    playlist = cursor.fetchone()

    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404

    if playlist.userId != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Permission denied"}), 403

    cursor.execute("SELECT id FROM Songs WHERE id = ?", (song_id,))
    song = cursor.fetchone()
    if not song:
        return jsonify({"error": "Song not found"}), 404

    cursor.execute(
        "SELECT 1 FROM PlaylistSongs WHERE playlistId = ? AND songId = ?",
        (playlist_id, song_id),
    )
    exists = cursor.fetchone()
    if exists:
        return jsonify({"message": "Song already in playlist"})

    cursor.execute(
        "INSERT INTO PlaylistSongs (playlistId, songId) VALUES (?, ?)",
        (playlist_id, song_id),
    )
    conn.commit()
    return jsonify({"message": "Song added to playlist"})


@app.route("/uploads/<filename>")
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
