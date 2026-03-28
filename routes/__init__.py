from .auth import auth_bp
from .library import library_bp
from .pages import pages_bp
from .playlists import playlists_bp
from .songs import songs_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(songs_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(playlists_bp)
    app.register_blueprint(pages_bp)
