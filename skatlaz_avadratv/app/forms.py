from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app import videos, thumbnails, audio

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        from app.models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        from app.models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class VideoUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Length(max=5000)])
    media_type = SelectField('Media Type', choices=[('video', 'Video'), ('audio', 'Music')])
    video_file = FileField('Video File', validators=[FileAllowed(videos, 'Videos only!')])
    audio_file = FileField('Audio File', validators=[FileAllowed(audio, 'Audio files only!')])
    thumbnail = FileField('Thumbnail (Optional)', validators=[FileAllowed(thumbnails, 'Images only!')])
    hashtags = StringField('Hashtags (comma separated)', validators=[Length(max=500)])
    license_type = SelectField('License', choices=[
        ('Standard YouTube License', 'Standard YouTube License'),
        ('Creative Commons', 'Creative Commons'),
        ('Public Domain', 'Public Domain'),
        ('All Rights Reserved', 'All Rights Reserved')
    ])
    region = SelectField('Region', choices=[
        ('US', 'United States'),
        ('BR', 'Brazil'),
        ('GB', 'United Kingdom'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('JP', 'Japan'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('ES', 'Spain'),
        ('IT', 'Italy'),
        ('Worldwide', 'Worldwide')
    ])
    is_published = BooleanField('Publish immediately', default=True)
    
    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        
        # Check that at least one file is uploaded
        if self.media_type.data == 'video' and not self.video_file.data:
            self.video_file.errors.append('Video file is required.')
            return False
        elif self.media_type.data == 'audio' and not self.audio_file.data:
            self.audio_file.errors.append('Audio file is required.')
            return False
        
        return True

class ChannelEditForm(FlaskForm):
    name = StringField('Channel Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=5000)])
    banner = FileField('Channel Banner', validators=[FileAllowed(thumbnails, 'Images only!')])
    custom_url = StringField('Custom URL', validators=[Length(max=100), Optional()])

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(max=1000)])

class PlaylistForm(FlaskForm):
    name = StringField('Playlist Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    is_public = BooleanField('Make Public', default=True)
