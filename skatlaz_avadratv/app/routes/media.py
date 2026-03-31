import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, jsonify
from flask_login import login_required, current_user
from app import db, videos, thumbnails, audio
from app.models import Video, Comment, Like, View
from app.forms import VideoUploadForm, CommentForm
from werkzeug.utils import secure_filename
from datetime import datetime
import json

bp = Blueprint('media', __name__)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = VideoUploadForm()
    
    if form.validate_on_submit():
        # Generate unique filename
        file_ext = ''
        filename = ''
        
        if form.media_type.data == 'video':
            file = form.video_file.data
            file_ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{file_ext}"
            file.save(os.path.join(current_app.config['UPLOADED_VIDEOS_DEST'], filename))
        else:
            file = form.audio_file.data
            file_ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{file_ext}"
            file.save(os.path.join(current_app.config['UPLOADED_AUDIO_DEST'], filename))
        
        # Handle thumbnail
        thumbnail_filename = 'default_thumbnail.jpg'
        if form.thumbnail.data:
            thumb_file = form.thumbnail.data
            thumb_ext = os.path.splitext(thumb_file.filename)[1]
            thumbnail_filename = f"{uuid.uuid4().hex}{thumb_ext}"
            thumb_file.save(os.path.join(current_app.config['UPLOADED_THUMBNAILS_DEST'], thumbnail_filename))
        
        # Get video duration (would need ffmpeg or moviepy)
        duration = 0
        
        video = Video(
            title=form.title.data,
            description=form.description.data,
            filename=filename,
            thumbnail=thumbnail_filename,
            duration=duration,
            media_type=form.media_type.data,
            hashtags=form.hashtags.data,
            license_type=form.license_type.data,
            region=form.region.data,
            is_published=form.is_published.data,
            user_id=current_user.id,
            channel_id=current_user.channel.id
        )
        
        db.session.add(video)
        db.session.commit()
        
        flash('Video uploaded successfully!', 'success')
        return redirect(url_for('media.watch', video_id=video.id))
    
    return render_template('upload.html', form=form)

@bp.route('/watch/<int:video_id>')
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    
    if not video.is_published:
        if not current_user.is_authenticated or current_user.id != video.user_id:
            abort(404)
    
    # Get user's like status
    user_like = None
    if current_user.is_authenticated:
        user_like = Like.query.filter_by(user_id=current_user.id, video_id=video_id).first()
    
    # Get comments
    comments = video.comments.filter_by(parent_id=None).order_by(Comment.created_at.desc()).all()
    
    # Get recommendations
    recommendations = Video.query.filter(
        Video.is_published == True,
        Video.id != video_id
    ).order_by(Video.views.desc()).limit(10).all()
    
    return render_template('watch.html', 
                         video=video, 
                         user_like=user_like,
                         comments=comments,
                         recommendations=recommendations)

@bp.route('/edit/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit(video_id):
    video = Video.query.get_or_404(video_id)
    
    if video.user_id != current_user.id:
        abort(403)
    
    form = VideoUploadForm()
    
    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.description.data
        video.hashtags = form.hashtags.data
        video.license_type = form.license_type.data
        video.region = form.region.data
        video.is_published = form.is_published.data
        
        db.session.commit()
        flash('Video updated successfully!', 'success')
        return redirect(url_for('media.watch', video_id=video.id))
    
    # Pre-populate form
    form.title.data = video.title
    form.description.data = video.description
    form.hashtags.data = video.hashtags
    form.license_type.data = video.license_type
    form.region.data = video.region
    form.is_published.data = video.is_published
    
    return render_template('edit_video.html', form=form, video=video)

@bp.route('/delete/<int:video_id>', methods=['POST'])
@login_required
def delete(video_id):
    video = Video.query.get_or_404(video_id)
    
    if video.user_id != current_user.id:
        abort(403)
    
    # Delete files
    try:
        if video.media_type == 'video':
            os.remove(os.path.join(current_app.config['UPLOADED_VIDEOS_DEST'], video.filename))
        else:
            os.remove(os.path.join(current_app.config['UPLOADED_AUDIO_DEST'], video.filename))
        
        if video.thumbnail != 'default_thumbnail.jpg':
            os.remove(os.path.join(current_app.config['UPLOADED_THUMBNAILS_DEST'], video.thumbnail))
    except:
        pass
    
    db.session.delete(video)
    db.session.commit()
    
    flash('Video deleted successfully.', 'success')
    return redirect(url_for('channel.view', username=current_user.username))
