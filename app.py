import os
import sys

from flask import Flask

if __package__ in (None, ""):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from MusicApp.routes import register_blueprints
else:
    from .routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = "uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    register_blueprints(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
