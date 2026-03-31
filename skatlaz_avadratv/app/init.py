from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import configure_uploads, UploadSet, IMAGES, VIDEOS
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'

# Configure uploads
videos = UploadSet('videos', ('mp4', 'avi', 'mov', 'mkv', 'webm'))
thumbnails = UploadSet('thumbnails', IMAGES)
audio = UploadSet('audio', ('mp3', 'wav', 'ogg', 'm4a'))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure uploads
    configure_uploads(app, (videos, thumbnails, audio))
    
    # Register blueprints
    from app.routes import main, auth, media, channel, player
    from app.api import auth as api_auth, media as api_media, player as api_player, search as api_search
    
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(media.bp)
    app.register_blueprint(channel.bp)
    app.register_blueprint(player.bp)
    
    # API routes
    app.register_blueprint(api_auth.bp)
    app.register_blueprint(api_media.bp)
    app.register_blueprint(api_player.bp)
    app.register_blueprint(api_search.bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
