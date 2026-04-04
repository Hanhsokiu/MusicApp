from flask import jsonify


def get_response(data, status_code=200):
    response = jsonify(data)
    response.status_code = status_code
    return response


def get_list_result(cursor):
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
