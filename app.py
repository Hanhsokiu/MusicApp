from flask import Flask

from routes import register_blueprints
from routes.common import UPLOAD_FOLDER


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

register_blueprints(app)


if __name__ == "__main__":
    app.run(debug=True)
