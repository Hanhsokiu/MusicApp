from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time
import pyodbc


conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-23HSO403\\SQLEXPRESS;"
    "DATABASE=MusicApp;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()


app = Flask(__name__)
CORS(app)



UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== PHÂN QUYỀN =====
def is_admin(role):
    return role == "admin"

#========================================================================================
# Get songs
@app.route('/api/songs', methods=['GET'])
def get_songs():
    userId = request.args.get("userId")

    cursor.execute("""
        SELECT s.*, 
               CASE WHEN f.songId IS NOT NULL THEN 1 ELSE 0 END AS isFavorite
        FROM Songs s
        LEFT JOIN Favorites f 
        ON s.id = f.songId AND f.userId = ?
    """, (userId,))

    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "title": row.title,
            "artist": row.artist,
            "fileUrl": row.fileUrl,
            "imageUrl": row.imageUrl,
            "isFavorite": row.isFavorite
        })

    return jsonify(data)
#========================================================================================
# Upload (Admin only)
@app.route('/api/songs', methods=['POST'])
def upload_song():
    role = request.headers.get("role")

    if not is_admin(role):
        return jsonify({"error": "Permission denied"}), 403

    if 'song' not in request.files:
        return jsonify({"error": "No song file"}), 400

    song_file = request.files['song']
    image_file = request.files.get('image')

    title = request.form.get('title')
    artist = request.form.get('artist')

    # Save song
    song_filename = str(int(time.time())) + "_" + song_file.filename
    song_path = os.path.join(UPLOAD_FOLDER, song_filename)
    song_file.save(song_path)

    fileUrl = "/uploads/" + song_filename
    # ========================================================================================
    # Save image
    imageUrl = None
    if image_file:
        image_filename = "img_" + str(int(time.time())) + "_" + image_file.filename
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image_file.save(image_path)
        imageUrl = "/uploads/" + image_filename

    # Save DB
    cursor.execute(
        "INSERT INTO Songs (title, artist, fileUrl, imageUrl) VALUES (?, ?, ?, ?)",
        (title, artist, fileUrl, imageUrl)
    )
    conn.commit()

    return jsonify({"message": "Upload success"})

#========================================================================================
# Search
@app.route('/api/songs/search')
def search_song():
    q = request.args.get('q', '')

    cursor.execute(
        "SELECT * FROM Songs WHERE title LIKE ?",
        ('%' + q + '%',)
    )
    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "title": row.title,
            "artist": row.artist,
            "fileUrl": row.fileUrl,
            "imageUrl": row.imageUrl

        })

    return jsonify(data)
#========================================================================================
# Delete (Admin only)
@app.route('/api/songs/<int:id>', methods=['DELETE'])
def delete_song(id):
    role = request.headers.get("role")

    if not is_admin(role):
        return jsonify({"error": "Permission denied"}), 403

    cursor.execute("SELECT fileUrl, imageUrl FROM Songs WHERE id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Not found"}), 404

    # delete file
    if row.fileUrl:
        path = os.path.join(UPLOAD_FOLDER, row.fileUrl.replace("/uploads/", ""))
        if os.path.exists(path):
            os.remove(path)

    if row.imageUrl:
        path = os.path.join(UPLOAD_FOLDER, row.imageUrl.replace("/uploads/", ""))
        if os.path.exists(path):
            os.remove(path)

    cursor.execute("DELETE FROM Songs WHERE id = ?", (id,))
    conn.commit()

    return jsonify({"message": "Deleted"})
#========================================================================================
# Update (Admin only)
@app.route('/api/songs/<int:id>', methods=['PUT'])
def update_song(id):
    role = request.headers.get("role")

    if not is_admin(role):
        return jsonify({"error": "Permission denied"}), 403

    cursor.execute("SELECT * FROM Songs WHERE id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Not found"}), 404

    title = request.form.get('title')
    artist = request.form.get('artist')
    song_file = request.files.get('song')
    image_file = request.files.get('image')

    fileUrl = row.fileUrl
    imageUrl = row.imageUrl

    if song_file:
        name = str(int(time.time())) + "_" + song_file.filename
        path = os.path.join(UPLOAD_FOLDER, name)
        song_file.save(path)
        fileUrl = "/uploads/" + name

    if image_file:
        name = "img_" + str(int(time.time())) + "_" + image_file.filename
        path = os.path.join(UPLOAD_FOLDER, name)
        image_file.save(path)
        imageUrl = "/uploads/" + name

    cursor.execute("""
        UPDATE Songs
        SET title=?, artist=?, fileUrl=?, imageUrl=?
        WHERE id=?
    """, (title, artist, fileUrl, imageUrl, id))
    conn.commit()
    return jsonify({"message": "Updated"})
#========================================================================================
# Register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing data"}), 400

    hashed = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, "user")
        )
        conn.commit()
        return jsonify({"message": "Register success"})
    except:
        return jsonify({"error": "Username exists"}), 400

#=========================
# Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user.password, password):
        return jsonify({
            "message": "Login success",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        })

    return jsonify({"error": "Invalid login"}), 401
#========================================================================================
@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    userId = request.json.get("userId")
    songId = request.json.get("songId")

    # 🔍 kiểm tra tồn tại
    cursor.execute(
        "SELECT * FROM Favorites WHERE userId=? AND songId=?",
        (userId, songId)
    )
    exists = cursor.fetchone()

    if exists:
        return jsonify({"message": "Already liked"})

    # ✅ thêm nếu chưa có
    cursor.execute(
        "INSERT INTO Favorites (userId, songId) VALUES (?, ?)",
        (userId, songId)
    )
    conn.commit()

    return jsonify({"message": "Added"})
#========================================================================================
@app.route('/api/favorites', methods=['DELETE'])
def remove_favorite():
    userId = request.json.get("userId")
    songId = request.json.get("songId")

    cursor.execute(
        "DELETE FROM Favorites WHERE userId=? AND songId=?",
        (userId, songId)
    )
    conn.commit()

    return jsonify({"message": "Removed"})
#========================================================================================
@app.route('/api/favorites/<int:userId>')
def get_favorites(userId):
    cursor.execute("""
        SELECT s.* FROM Songs s
        JOIN Favorites f ON s.id = f.songId
        WHERE f.userId = ?
    """, (userId,))

    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "title": row.title,
            "artist": row.artist,
            "fileUrl": row.fileUrl,
            "imageUrl": row.imageUrl,
            "isFavorite": 1
        })

    return jsonify(data)
#========================================================================================
@app.route('/api/recent', methods=['POST'])
def add_recent():
    userId = request.json.get("userId")
    songId = request.json.get("songId")

    cursor.execute(
        "INSERT INTO Recent (userId, songId) VALUES (?, ?)",
        (userId, songId)
    )
    conn.commit()

    return jsonify({"message": "Added recent"})
#========================================================================================
@app.route('/api/recent/<int:userId>')
def get_recent(userId):
    cursor.execute("""
        SELECT TOP 10 s.* FROM Songs s
        JOIN Recent r ON s.id = r.songId
        WHERE r.userId = ?
        ORDER BY r.playedAt DESC
    """, (userId,))

    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "title": row.title,
            "artist": row.artist,
            "fileUrl": row.fileUrl,
            "imageUrl": row.imageUrl
        })

    return jsonify(data)
#========================================================================================
#========================================================================================
@app.route('/api/favorites/toggle', methods=['POST'])
def toggle_favorite():
    userId = request.json.get("userId")
    songId = request.json.get("songId")

    # 🔍 kiểm tra đã tồn tại chưa
    cursor.execute(
        "SELECT * FROM Favorites WHERE userId=? AND songId=?",
        (userId, songId)
    )
    exists = cursor.fetchone()

    if exists:

        cursor.execute(
            "DELETE FROM Favorites WHERE userId=? AND songId=?",
            (userId, songId)
        )
        conn.commit()
        return jsonify({"status": "removed"})
    else:
        # ✅ chưa có → thêm
        cursor.execute(
            "INSERT INTO Favorites (userId, songId) VALUES (?, ?)",
            (userId, songId)
        )
        conn.commit()
        return jsonify({"status": "added"})
#========================================================================================
#========================================================================================
#========================================================================================

#========================================================================================

#STATIC + PAGES
@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/login')
def login_page():
    return render_template('login.html')
@app.route('/register')
def register_page():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)