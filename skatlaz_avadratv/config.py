import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'skatzla.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOADED_VIDEOS_DEST = os.path.join(basedir, 'app', 'static', 'uploads', 'videos')
    UPLOADED_THUMBNAILS_DEST = os.path.join(basedir, 'app', 'static', 'uploads', 'thumbnails')
    UPLOADED_AUDIO_DEST = os.path.join(basedir, 'app', 'static', 'uploads', 'audio')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'}
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
