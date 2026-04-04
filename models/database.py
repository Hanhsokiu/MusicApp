import pyodbc


CN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-23HSO403\\SQLEXPRESS;"
    "DATABASE=MusicApp;"
    "Trusted_Connection=yes;"
)


def get_connection():
    return pyodbc.connect(CN_STR)
