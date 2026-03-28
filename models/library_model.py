from .database import get_connection, get_list_result


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


def get_favorites_by_user(user_id):
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
        return get_list_result(cursor)
    finally:
        conn.close()


def add_recent(user_id, song_id):
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


def get_recent_by_user(user_id):
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
        return get_list_result(cursor)
    finally:
        conn.close()

