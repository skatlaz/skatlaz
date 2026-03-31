from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='default_avatar.png')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    channel = db.relationship('Channel', backref='owner', uselist=False, cascade='all, delete-orphan')
    videos = db.relationship('Video', backref='uploader', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    views = db.relationship('View', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Channel(db.Model):
    __tablename__ = 'channels'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    banner = db.Column(db.String(200), default='default_banner.jpg')
    custom_url = db.Column(db.String(100), unique=True)
    subscribers = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    videos = db.relationship('Video', backref='channel', lazy='dynamic')
    playlists = db.relationship('Playlist', backref='channel', lazy='dynamic')
    
    def __repr__(self):
        return f'<Channel {self.name}>'

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200), nullable=False)
    thumbnail = db.Column(db.String(200), default='default_thumbnail.jpg')
    duration = db.Column(db.Integer, default=0)  # seconds
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    media_type = db.Column(db.String(20), default='video')  # video, audio
    hashtags = db.Column(db.String(500))  # comma separated
    license_type = db.Column(db.String(50), default='Standard YouTube License')
    region = db.Column(db.String(10), default='US')
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    likes_relation = db.relationship('Like', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    views_relation = db.relationship('View', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_hashtags_list(self):
        if self.hashtags:
            return [tag.strip() for tag in self.hashtags.split(',')]
        return []
    
    def add_view(self, user_id=None, ip=None):
        view = View(video_id=self.id, user_id=user_id, ip=ip)
        db.session.add(view)
        self.views += 1
        db.session.commit()
    
    def __repr__(self):
        return f'<Video {self.title}>'

class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    
    # Many-to-many relationship with videos
    videos = db.relationship('Video', secondary='playlist_videos', backref='playlists')
    
class PlaylistVideo(db.Model):
    __tablename__ = 'playlist_videos'
    
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), primary_key=True)
    position = db.Column(db.Integer, default=0)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # Self-referential relationship for replies
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'

class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    is_like = db.Column(db.Boolean, nullable=True)  # True=like, False=dislike, None=neutral
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='unique_user_video_like'),)

class View(db.Model):
    __tablename__ = 'views'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)

class RemoteSession(db.Model):
    __tablename__ = 'remote_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(100), unique=True, nullable=False)
    device_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    current_video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=True)
    is_playing = db.Column(db.Boolean, default=False)
    current_time = db.Column(db.Float, default=0.0)
    volume = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def to_json(self):
        return {
            'session_token': self.session_token,
            'device_name': self.device_name,
            'is_active': self.is_active,
            'is_playing': self.is_playing,
            'current_time': self.current_time,
            'volume': self.volume,
            'current_video': {
                'id': self.current_video_id,
                'title': self.video.title if self.video else None
            } if self.current_video_id else None
        }
