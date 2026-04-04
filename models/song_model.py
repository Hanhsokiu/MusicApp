from models.database import get_connection


def _rows_to_dicts(cursor):
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def fetch_all_songs(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            select s.*,
                   case when f.songId is not null then 1 else 0 end as isFavorite
            from Songs s
            left join Favorites f on s.id = f.songId and f.userId = ?
            """,
            user_id,
        )
        return _rows_to_dicts(cursor)
    finally:
        conn.close()


def search_songs(query):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select * from Songs where title like ?", "%" + query + "%")
        return _rows_to_dicts(cursor)
    finally:
        conn.close()


def insert_song(title, artist, file_url, image_url):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "insert into Songs(title, artist, fileUrl, imageUrl) values(?, ?, ?, ?)",
            (title, artist, file_url, image_url),
        )
        conn.commit()
    finally:
        conn.close()


def get_song_by_id(song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select * from Songs where id = ?", song_id)
        return cursor.fetchone()
    finally:
        conn.close()


def update_song(song_id, title, artist, file_url, image_url):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "update Songs set title = ?, artist = ?, fileUrl = ?, imageUrl = ? where id = ?",
            (title, artist, file_url, image_url, song_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_song_relations(song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("delete from PlaylistSongs where songId = ?", song_id)
        cursor.execute("delete from Favorites where songId = ?", song_id)
        cursor.execute("delete from Recent where songId = ?", song_id)
        cursor.execute("delete from Songs where id = ?", song_id)
        conn.commit()
    finally:
        conn.close()


def fetch_song_for_download(song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select title, artist, fileUrl from Songs where id = ?", song_id)
        return cursor.fetchone()
    finally:
        conn.close()
