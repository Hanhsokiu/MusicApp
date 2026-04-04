import os
import re
import time

from flask import Blueprint, current_app, send_from_directory
from werkzeug.utils import secure_filename

from routes.response import get_response


common_bp = Blueprint("common", __name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_admin(role):
    return role == "admin"


def build_download_name(song):
    extension = os.path.splitext(song.fileUrl or "")[1] or ".mp3"
    raw_name = f"{song.title} - {song.artist}{extension}"
    sanitized = re.sub(r'[\\/:*?"<>|]+', "_", raw_name).strip()
    return sanitized or f"song{extension}"


def save_uploaded_file(file_storage, prefix=""):
    filename = secure_filename(file_storage.filename or "")
    stored_name = f"{prefix}{int(time.time())}_{filename}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_storage.save(os.path.join(upload_folder, stored_name))
    return f"/uploads/{stored_name}"


def remove_uploaded_file(file_url):
    if not file_url:
        return
    filename = file_url.replace("/uploads/", "", 1)
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        os.remove(file_path)


@common_bp.route("/uploads/<filename>", methods=["GET"])
def get_file(filename):
    try:
        return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
    except Exception as exc:
        print(exc)
        return get_response({"error": "Khong lay duoc file"}, 404)
