from flask import Blueprint, current_app, render_template, send_from_directory

from .response import get_response


pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/uploads/<filename>", methods=["GET"])
def get_file(filename):
    try:
        return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
    except Exception as error:
        print(error)
        return get_response({"error": "Khong lay duoc file"}, 404)


@pages_bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@pages_bp.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html")


@pages_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@pages_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")
