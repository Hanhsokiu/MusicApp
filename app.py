from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import time
import pyodbc

conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=DESKTOP-OF-HANH\\SQLEXPRESS;"
    "Database=MusicApp;"
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
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['song']
    title = request.form.get('title')
    artist = request.form.get('artist')

    filename = str(int(time.time())) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    fileUrl = "/uploads/" + filename

    # 🔥 Lưu vào SQL Server
    cursor.execute(
        "INSERT INTO Songs (title, artist, fileUrl) VALUES (?, ?, ?)",
        (title, artist, fileUrl)
    )
    conn.commit()

    return jsonify({
        "title": title,
        "artist": artist,
        "fileUrl": fileUrl
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
            "fileUrl": row.fileUrl
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
            "fileUrl": row.fileUrl
        })

    return jsonify(songs)
# Lấy file nhạc
@app.route('/uploads/<filename>')
def get_song(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def home():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)