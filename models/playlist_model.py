from models.database import get_connection


def fetch_playlists(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            select p.id, p.name, count(ps.songId) as songCount
            from Playlists p
            left join PlaylistSongs ps on p.id = ps.playlistId
            where p.userId = ?
            group by p.id, p.name, p.createdAt
            order by p.createdAt desc
            """,
            user_id,
        )
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def create_playlist(user_id, name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "insert into Playlists(userId, name) values(?, ?)",
            (user_id, name),
        )
        conn.commit()
        cursor.execute(
            "select top 1 id, name from Playlists where userId = ? order by id desc",
            user_id,
        )
        return cursor.fetchone()
    finally:
        conn.close()


def get_playlist_for_user(playlist_id, user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "select * from Playlists where id = ? and userId = ?",
            (playlist_id, user_id),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def fetch_playlist_songs(playlist_id, user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            select s.*,
                   case when f.songId is not null then 1 else 0 end as isFavorite
            from PlaylistSongs ps
            join Songs s on s.id = ps.songId
            left join Favorites f on s.id = f.songId and f.userId = ?
            where ps.playlistId = ?
            order by ps.addedAt asc, ps.id asc
            """,
            (user_id, playlist_id),
        )
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def get_playlist_song(playlist_id, song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "select * from PlaylistSongs where playlistId = ? and songId = ?",
            (playlist_id, song_id),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def add_song_to_playlist(playlist_id, song_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "insert into PlaylistSongs(playlistId, songId) values(?, ?)",
            (playlist_id, song_id),
        )
        conn.commit()
    finally:
        conn.close()
