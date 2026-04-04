from flask import Blueprint, render_template


pages_bp = Blueprint("pages", __name__)


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
