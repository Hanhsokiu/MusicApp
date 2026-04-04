from routes.auth import auth_bp
from routes.common import common_bp
from routes.library import library_bp
from routes.pages import pages_bp
from routes.playlists import playlists_bp
from routes.songs import songs_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(playlists_bp)
    app.register_blueprint(songs_bp)
