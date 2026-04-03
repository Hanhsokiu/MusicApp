import os
import re
import time

import flask
import pyodbc
from werkzeug.security import check_password_hash, generate_password_hash


cn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-23HSO403\\SQLEXPRESS;"
    "DATABASE=MusicApp;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(cn_str)
app = flask.Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_admin(role):
    return role == "admin"


def get_response(data, status_code=200):
    resp = flask.jsonify(data)
    resp.status_code = status_code
    return resp


def get_list_result(cursor):
    results = []
    keys = []
    for item in cursor.description:
        keys.append(item[0])
    for value in cursor.fetchall():
        results.append(dict(zip(keys, value)))
    return results


def build_download_name(song):
    extension = os.path.splitext(song.fileUrl or "")[1] or ".mp3"
    raw_name = f"{song.title} - {song.artist}{extension}"
    sanitized = re.sub(r'[\\/:*?"<>|]+', "_", raw_name).strip()
    return sanitized or f"song{extension}"


@app.route('/api/songs', methods=['GET'])
def get_all_song():
    try:
        user_id = flask.request.args.get("userId")
        cursor = conn.cursor()
        cursor.execute("""
            select s.*,
                   case when f.songId is not null then 1 else 0 end as isFavorite
            from Songs s
            left join Favorites f on s.id = f.songId and f.userId = ?
        """, user_id)
        return get_response(get_list_result(cursor))
    except Exception as e:
        print(e)
        return get_response({"error": "Không lấy được danh sách bài hát"}, 500)


@app.route('/api/songs/search', methods=['GET'])
def search_song():
    try:
        q = flask.request.args.get("q", "")
        cursor = conn.cursor()
        cursor.execute("select * from Songs where title like ?", "%" + q + "%")
        return get_response(get_list_result(cursor))
    except Exception as e:
        print(e)
        return get_response({"error": "Không tìm kiếm được bài hát"}, 500)


@app.route('/api/songs', methods=['POST'])
def add_song():
    try:
        role = flask.request.headers.get("role")
        if not is_admin(role):
            return get_response({"error": "Permission denied"}, 403)

        if 'song' not in flask.request.files:
            return get_response({"error": "No song file"}, 400)

        title = flask.request.form.get("title")
        artist = flask.request.form.get("artist")
        song_file = flask.request.files['song']
        image_file = flask.request.files.get('image')

        song_filename = str(int(time.time())) + "_" + song_file.filename
        song_path = os.path.join(UPLOAD_FOLDER, song_filename)
        song_file.save(song_path)
        file_url = "/uploads/" + song_filename

        image_url = None
        if image_file:
            image_filename = "img_" + str(int(time.time())) + "_" + image_file.filename
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            image_file.save(image_path)
            image_url = "/uploads/" + image_filename

        cursor = conn.cursor()
        sql = "insert into Songs(title, artist, fileUrl, imageUrl) values(?, ?, ?, ?)"
        data = (title, artist, file_url, image_url)
        cursor.execute(sql, data)
        conn.commit()
        return get_response({"message": "Upload success"})
    except Exception as e:
        print(e)
        return get_response({"error": "Upload thất bại"}, 500)


@app.route('/api/songs/<id>', methods=['PUT'])
def update_song(id):
    try:
        role = flask.request.headers.get("role")
        if not is_admin(role):
            return get_response({"error": "Permission denied"}, 403)

        cursor = conn.cursor()
        cursor.execute("select * from Songs where id = ?", id)
        song = cursor.fetchone()
        if not song:
            return get_response({"error": "Not found"}, 404)

        title = flask.request.form.get("title")
        artist = flask.request.form.get("artist")
        song_file = flask.request.files.get("song")
        image_file = flask.request.files.get("image")

        file_url = song.fileUrl
        image_url = song.imageUrl

        if song_file:
            song_filename = str(int(time.time())) + "_" + song_file.filename
            song_path = os.path.join(UPLOAD_FOLDER, song_filename)
            song_file.save(song_path)
            file_url = "/uploads/" + song_filename

        if image_file:
            image_filename = "img_" + str(int(time.time())) + "_" + image_file.filename
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            image_file.save(image_path)
            image_url = "/uploads/" + image_filename

        sql = "update Songs set title = ?, artist = ?, fileUrl = ?, imageUrl = ? where id = ?"
        data = (title, artist, file_url, image_url, id)
        cursor.execute(sql, data)
        conn.commit()
        return get_response({"message": "Updated"})
    except Exception as e:
        print(e)
        return get_response({"error": "Cập nhật thất bại"}, 500)


@app.route('/api/songs/<id>', methods=['DELETE'])
def delete_song(id):
    try:
        role = flask.request.headers.get("role")
        if not is_admin(role):
            return get_response({"error": "Permission denied"}, 403)

        cursor = conn.cursor()
        cursor.execute("select fileUrl, imageUrl from Songs where id = ?", id)
        song = cursor.fetchone()
        if not song:
            return get_response({"error": "Not found"}, 404)

        if song.fileUrl:
            song_path = os.path.join(UPLOAD_FOLDER, song.fileUrl.replace("/uploads/", ""))
            if os.path.exists(song_path):
                os.remove(song_path)

        if song.imageUrl:
            image_path = os.path.join(UPLOAD_FOLDER, song.imageUrl.replace("/uploads/", ""))
            if os.path.exists(image_path):
                os.remove(image_path)

        cursor.execute("delete from PlaylistSongs where songId = ?", id)
        cursor.execute("delete from Favorites where songId = ?", id)
        cursor.execute("delete from Recent where songId = ?", id)
        cursor.execute("delete from Songs where id = ?", id)
        conn.commit()
        return get_response({"message": "Deleted"})
    except Exception as e:
        print(e)
        return get_response({"error": "Xóa thất bại"}, 500)


@app.route('/api/register', methods=['POST'])
def register():
    try:
        username = flask.request.json.get("username")
        password = flask.request.json.get("password")

        if not username or not password:
            return get_response({"error": "Missing data"}, 400)

        hashed_password = generate_password_hash(password)
        cursor = conn.cursor()
        sql = "insert into Users(username, password, role) values(?, ?, ?)"
        data = (username, hashed_password, "user")
        cursor.execute(sql, data)
        conn.commit()
        return get_response({"message": "Register success"})
    except Exception as e:
        print(e)
        return get_response({"error": "Username exists"}, 400)


@app.route('/api/login', methods=['POST'])
def login():
    try:
        username = flask.request.json.get("username")
        password = flask.request.json.get("password")

        cursor = conn.cursor()
        cursor.execute("select * from Users where username = ?", username)
        user = cursor.fetchone()

        if user and check_password_hash(user.password, password):
            return get_response({
                "message": "Login success",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role
                }
            })

        return get_response({"error": "Invalid login"}, 401)
    except Exception as e:
        print(e)
        return get_response({"error": "Đăng nhập thất bại"}, 500)


@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    try:
        user_id = flask.request.json.get("userId")
        song_id = flask.request.json.get("songId")

        cursor = conn.cursor()
        cursor.execute("select * from Favorites where userId = ? and songId = ?", (user_id, song_id))
        favorite = cursor.fetchone()
        if favorite:
            return get_response({"message": "Already liked"})

        sql = "insert into Favorites(userId, songId) values(?, ?)"
        data = (user_id, song_id)
        cursor.execute(sql, data)
        conn.commit()
        return get_response({"message": "Added"})
    except Exception as e:
        print(e)
        return get_response({"error": "Thêm yêu thích thất bại"}, 500)


@app.route('/api/favorites', methods=['DELETE'])
def remove_favorite():
    try:
        user_id = flask.request.json.get("userId")
        song_id = flask.request.json.get("songId")

        cursor = conn.cursor()
        sql = "delete from Favorites where userId = ? and songId = ?"
        data = (user_id, song_id)
        cursor.execute(sql, data)
        conn.commit()
        return get_response({"message": "Removed"})
    except Exception as e:
        print(e)
        return get_response({"error": "Xóa yêu thích thất bại"}, 500)


@app.route('/api/favorites/<id>', methods=['GET'])
def get_favorite_by_user(id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            select s.*, 1 as isFavorite
            from Songs s
            join Favorites f on s.id = f.songId
            where f.userId = ?
        """, id)
        return get_response(get_list_result(cursor))
    except Exception as e:
        print(e)
        return get_response({"error": "Không lấy được danh sách yêu thích"}, 500)


@app.route('/api/favorites/toggle', methods=['POST'])
def toggle_favorite():
    try:
        user_id = flask.request.json.get("userId")
        song_id = flask.request.json.get("songId")

        cursor = conn.cursor()
        cursor.execute("select * from Favorites where userId = ? and songId = ?", (user_id, song_id))
        favorite = cursor.fetchone()

        if favorite:
            cursor.execute("delete from Favorites where userId = ? and songId = ?", (user_id, song_id))
            conn.commit()
            return get_response({"status": "removed"})

        cursor.execute("insert into Favorites(userId, songId) values(?, ?)", (user_id, song_id))
        conn.commit()
        return get_response({"status": "added"})
    except Exception as e:
        print(e)
        return get_response({"error": "Cập nhật yêu thích thất bại"}, 500)


@app.route('/api/recent', methods=['POST'])
def add_recent():
    try:
        user_id = flask.request.json.get("userId")
        song_id = flask.request.json.get("songId")

        cursor = conn.cursor()
        sql = "insert into Recent(userId, songId) values(?, ?)"
        data = (user_id, song_id)
        cursor.execute(sql, data)
        conn.commit()
        return get_response({"message": "Added recent"})
    except Exception as e:
        print(e)
        return get_response({"error": "Không thêm được recent"}, 500)


@app.route('/api/recent/<id>', methods=['GET'])
def get_recent(id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            select top 10 s.*
            from Songs s
            join Recent r on s.id = r.songId
            where r.userId = ?
            order by r.playedAt desc
        """, id)
        return get_response(get_list_result(cursor))
    except Exception as e:
        print(e)
        return get_response({"error": "Không lấy được recent"}, 500)


@app.route('/api/playlists', methods=['GET'])
def get_all_playlist():
    try:
        user_id = flask.request.args.get("userId")
        cursor = conn.cursor()
        cursor.execute("""
            select p.id, p.name, count(ps.songId) as songCount
            from Playlists p
            left join PlaylistSongs ps on p.id = ps.playlistId
            where p.userId = ?
            group by p.id, p.name, p.createdAt
            order by p.createdAt desc
        """, user_id)
        return get_response(get_list_result(cursor))
    except Exception as e:
        print(e)
        return get_response({"error": "Không lấy được playlist"}, 500)


@app.route('/api/playlists', methods=['POST'])
def add_playlist():
    try:
        user_id = flask.request.json.get("userId")
        name = (flask.request.json.get("name") or "").strip()

        if not user_id or not name:
            return get_response({"error": "Missing playlist data"}, 400)

        cursor = conn.cursor()
        sql = "insert into Playlists(userId, name) values(?, ?)"
        data = (user_id, name)
        cursor.execute(sql, data)
        conn.commit()

        cursor.execute("select top 1 id, name from Playlists where userId = ? order by id desc", user_id)
        playlist = cursor.fetchone()
        return get_response({
            "message": "Playlist created",
            "playlist": {
                "id": playlist.id,
                "name": playlist.name,
                "songCount": 0
            }
        })
    except Exception as e:
        print(e)
        return get_response({"error": "Tạo playlist thất bại"}, 500)


@app.route('/api/playlists/<playlist_id>/songs', methods=['GET'])
def get_song_by_playlist(playlist_id):
    try:
        user_id = flask.request.args.get("userId")
        cursor = conn.cursor()

        cursor.execute("select * from Playlists where id = ? and userId = ?", (playlist_id, user_id))
        playlist = cursor.fetchone()
        if not playlist:
            return get_response({"error": "Playlist not found"}, 404)

        cursor.execute("""
            select s.*,
                   case when f.songId is not null then 1 else 0 end as isFavorite
            from PlaylistSongs ps
            join Songs s on s.id = ps.songId
            left join Favorites f on s.id = f.songId and f.userId = ?
            where ps.playlistId = ?
            order by ps.addedAt asc, ps.id asc
        """, (user_id, playlist_id))
        return get_response(get_list_result(cursor))
    except Exception as e:
        print(e)
        return get_response({"error": "Không lấy được bài hát trong playlist"}, 500)


@app.route('/api/playlists/<playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    try:
        user_id = flask.request.json.get("userId")
        song_id = flask.request.json.get("songId")
        cursor = conn.cursor()

        cursor.execute("select * from Playlists where id = ? and userId = ?", (playlist_id, user_id))
        playlist = cursor.fetchone()
        if not playlist:
            return get_response({"error": "Playlist not found"}, 404)

        cursor.execute("select * from PlaylistSongs where playlistId = ? and songId = ?", (playlist_id, song_id))
        playlist_song = cursor.fetchone()
        if playlist_song:
            return get_response({"message": "Song already in playlist"})

        sql = "insert into PlaylistSongs(playlistId, songId) values(?, ?)"
        data = (playlist_id, song_id)
        cursor.execute(sql, data)
        conn.commit()
        return get_response({"message": "Song added to playlist"})
    except Exception as e:
        print(e)
        return get_response({"error": "Không thêm được bài hát vào playlist"}, 500)


@app.route('/api/songs/<id>/download', methods=['GET'])
def download_song(id):
    try:
        cursor = conn.cursor()
        cursor.execute("select title, artist, fileUrl from Songs where id = ?", id)
        song = cursor.fetchone()
        if not song or not song.fileUrl:
            return get_response({"error": "Song not found"}, 404)

        stored_filename = song.fileUrl.replace("/uploads/", "", 1)
        return flask.send_from_directory(
            UPLOAD_FOLDER,
            stored_filename,
            as_attachment=True,
            download_name=build_download_name(song)
        )
    except Exception as e:
        print(e)
        return get_response({"error": "KhÃ´ng táº£i Ä‘Æ°á»£c bÃ i hÃ¡t"}, 500)


@app.route('/uploads/<filename>', methods=['GET'])
def get_file(filename):
    try:
        return flask.send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(e)
        return get_response({"error": "Không lấy được file"}, 404)


@app.route('/', methods=['GET'])
def home():
    return flask.render_template('index.html')


@app.route('/upload', methods=['GET'])
def upload_page():
    return flask.render_template('upload.html')


@app.route('/login', methods=['GET'])
def login_page():
    return flask.render_template('login.html')


@app.route('/register', methods=['GET'])
def register_page():
    return flask.render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)
