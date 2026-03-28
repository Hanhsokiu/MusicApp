import pyodbc


CN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-OF-HANH\\SQLEXPRESS;"
    "DATABASE=MusicApp;"
    "Trusted_Connection=yes;"
)


def get_connection():
    return pyodbc.connect(CN_STR)


def get_list_result(cursor):
    keys = [item[0] for item in cursor.description]
    return [dict(zip(keys, value)) for value in cursor.fetchall()]

