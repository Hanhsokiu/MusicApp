from models.database import get_connection


def create_user(username, hashed_password, role="user"):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "insert into Users(username, password, role) values(?, ?, ?)",
            (username, hashed_password, role),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select * from Users where username = ?", username)
        return cursor.fetchone()
    finally:
        conn.close()
