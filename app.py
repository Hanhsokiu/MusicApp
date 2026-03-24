from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
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

songs = []  # fake database (sau sẽ thay bằng MongoDB)

# Upload bài hát
@app.route('/api/songs', methods=['POST'])
def upload_song():
    if 'song' not in request.files:
        return jsonify({"error": "No song file uploaded"}), 400

    song_file = request.files['song']
    image_file = request.files.get('image')  # 👈 ảnh (optional)

    title = request.form.get('title')
    artist = request.form.get('artist')

    # ====== Lưu file nhạc ======
    song_filename = str(int(time.time())) + "_" + song_file.filename
    song_path = os.path.join(UPLOAD_FOLDER, song_filename)
    song_file.save(song_path)

    fileUrl = "/uploads/" + song_filename

    # ====== Lưu ảnh ======
    imageUrl = None
    if image_file:
        image_filename = "img_" + str(int(time.time())) + "_" + image_file.filename
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image_file.save(image_path)

        imageUrl = "/uploads/" + image_filename

    # ====== Lưu DB ======
    cursor.execute(
        "INSERT INTO Songs (title, artist, fileUrl, imageUrl) VALUES (?, ?, ?, ?)",
        (title, artist, fileUrl, imageUrl)
    )
    conn.commit()

    return jsonify({
        "title": title,
        "artist": artist,
        "fileUrl": fileUrl,
        "imageUrl": imageUrl
    })

# Lấy danh sách bài hát
@app.route('/api/songs', methods=['GET'])
def get_songs():
    cursor.execute("SELECT * FROM Songs")
    rows = cursor.fetchall()

    songs = []
    for row in rows:
        songs.append({
            "id": row.id,
            "title": row.title,
            "artist": row.artist,
            "fileUrl": row.fileUrl,
            "imageUrl": row.imageUrl
        })

    return jsonify(songs)
@app.route('/api/songs/search')
def search_song():
    q = request.args.get('q')

    cursor.execute(
        "SELECT * FROM Songs WHERE title LIKE ?",
        ('%' + q + '%',)
    )
    rows = cursor.fetchall()

    songs = []
    for row in rows:
        songs.append({
            "id": row.id,
            "title": row.title,
            "artist": row.artist,
            "fileUrl": row.fileUrl,
            "imageUrl": row.imageUrl
        })

    return jsonify(songs)

# Xóa
@app.route('/api/songs/<int:id>', methods=['DELETE'])
def delete_song(id):
    # Lấy file để xóa khỏi ổ đĩa
    cursor.execute("SELECT fileUrl, imageUrl FROM Songs WHERE id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Song not found"}), 404

    # Xóa file nhạc
    if row.fileUrl:
        file_path = row.fileUrl.replace("/uploads/", "")
        full_path = os.path.join(UPLOAD_FOLDER, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    # Xóa ảnh
    if row.imageUrl:
        img_path = row.imageUrl.replace("/uploads/", "")
        full_img_path = os.path.join(UPLOAD_FOLDER, img_path)
        if os.path.exists(full_img_path):
            os.remove(full_img_path)

    # Xóa DB
    cursor.execute("DELETE FROM Songs WHERE id = ?", (id,))
    conn.commit()

    return jsonify({"message": "Deleted successfully"})
#Sửa
@app.route('/api/songs/<int:id>', methods=['PUT'])
def update_song(id):
    cursor.execute("SELECT * FROM Songs WHERE id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Song not found"}), 404

    title = request.form.get('title')
    artist = request.form.get('artist')
    song_file = request.files.get('song')
    image_file = request.files.get('image')

    fileUrl = row.fileUrl
    imageUrl = row.imageUrl

    # ====== Update file nhạc ======
    if song_file:
        song_filename = str(int(time.time())) + "_" + song_file.filename
        song_path = os.path.join(UPLOAD_FOLDER, song_filename)
        song_file.save(song_path)
        fileUrl = "/uploads/" + song_filename

    # ====== Update ảnh ======
    if image_file:
        image_filename = "img_" + str(int(time.time())) + "_" + image_file.filename
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image_file.save(image_path)
        imageUrl = "/uploads/" + image_filename

    # ====== Update DB ======
    cursor.execute("""
        UPDATE Songs
        SET title = ?, artist = ?, fileUrl = ?, imageUrl = ?
        WHERE id = ?
    """, (title, artist, fileUrl, imageUrl, id))

    conn.commit()

    return jsonify({"message": "Updated successfully"})
# Lấy file nhạc
@app.route('/uploads/<filename>')
def get_song(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def home():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)