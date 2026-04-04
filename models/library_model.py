from models.database import get_connection


def get_favorite(user_id, song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "select * from Favorites where userId = ? and songId = ?",
            (user_id, song_id),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def add_favorite(user_id, song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "insert into Favorites(userId, songId) values(?, ?)",
            (user_id, song_id),
        )
        conn.commit()
    finally:
        conn.close()


def remove_favorite(user_id, song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "delete from Favorites where userId = ? and songId = ?",
            (user_id, song_id),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_favorites_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            select s.*, 1 as isFavorite
            from Songs s
            join Favorites f on s.id = f.songId
            where f.userId = ?
            """,
            user_id,
        )
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def add_recent_song(user_id, song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "insert into Recent(userId, songId) values(?, ?)",
            (user_id, song_id),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_recent_songs(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            select top 10 s.*
            from Songs s
            join Recent r on s.id = r.songId
            where r.userId = ?
            order by r.playedAt desc
            """,
            user_id,
        )
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()
