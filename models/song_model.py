from .database import get_connection, get_list_result


def get_all_songs(user_id):
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
        return get_list_result(cursor)
    finally:
        conn.close()


def search_songs(keyword):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select * from Songs where title like ?", f"%{keyword}%")
        return get_list_result(cursor)
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


def create_song(title, artist, file_url, image_url):
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


def delete_song(song_id):
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

