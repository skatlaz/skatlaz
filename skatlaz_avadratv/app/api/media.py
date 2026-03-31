from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Video, Comment, Like, View
from datetime import datetime

bp = Blueprint('api_media', __name__, url_prefix='/api/media')

@bp.route('/video/<int:video_id>', methods=['GET'])
def get_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'thumbnail': video.thumbnail,
        'filename': video.filename,
        'duration': video.duration,
        'views': video.views,
        'likes': video.likes,
        'dislikes': video.dislikes,
        'media_type': video.media_type,
        'hashtags': video.get_hashtags_list(),
        'license_type': video.license_type,
        'region': video.region,
        'created_at': video.created_at.isoformat(),
        'uploader': {
            'id': video.uploader.id,
            'username': video.uploader.username,
            'avatar': video.uploader.avatar
        },
        'channel': {
            'id': video.channel.id,
            'name': video.channel.name,
            'subscribers': video.channel.subscribers
        }
    })

@bp.route('/like', methods=['POST'])
@login_required
def like_video():
    data = request.get_json()
    video_id = data.get('video_id')
    is_like = data.get('is_like', True)
    
    video = Video.query.get_or_404(video_id)
    
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        video_id=video_id
    ).first()
    
    if existing_like:
        if existing_like.is_like == is_like:
            # Remove like/dislike
            if existing_like.is_like:
                video.likes -= 1
            else:
                video.dislikes -= 1
            db.session.delete(existing_like)
        else:
            # Change from like to dislike or vice versa
            if is_like:
                video.likes += 1
                video.dislikes -= 1
            else:
                video.likes -= 1
                video.dislikes += 1
            existing_like.is_like = is_like
    else:
        # New like/dislike
        like = Like(user_id=current_user.id, video_id=video_id, is_like=is_like)
        db.session.add(like)
        if is_like:
            video.likes += 1
        else:
            video.dislikes += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'likes': video.likes,
        'dislikes': video.dislikes
    })

@bp.route('/comment', methods=['POST'])
@login_required
def add_comment():
    data = request.get_json()
    video_id = data.get('video_id')
    content = data.get('content')
    parent_id = data.get('parent_id')
    
    video = Video.query.get_or_404(video_id)
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        video_id=video_id,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': current_user.username,
            'created_at': comment.created_at.isoformat(),
            'likes': comment.likes
        }
    })

@bp.route('/comments/<int:video_id>', methods=['GET'])
def get_comments(video_id):
    video = Video.query.get_or_404(video_id)
    
    comments = video.comments.filter_by(parent_id=None)\
        .order_by(Comment.created_at.desc()).all()
    
    def serialize_comment(comment):
        return {
            'id': comment.id,
            'content': comment.content,
            'likes': comment.likes,
            'created_at': comment.created_at.isoformat(),
            'author': {
                'id': comment.author.id,
                'username': comment.author.username,
                'avatar': comment.author.avatar
            },
            'replies': [serialize_comment(reply) for reply in comment.replies]
        }
    
    return jsonify([serialize_comment(c) for c in comments])

@bp.route('/view', methods=['POST'])
def track_view():
    data = request.get_json()
    video_id = data.get('video_id')
    
    video = Video.query.get_or_404(video_id)
    
    view = View(
        video_id=video_id,
        user_id=current_user.id if current_user.is_authenticated else None,
        ip=request.remote_addr
    )
    
    db.session.add(view)
    video.views += 1
    db.session.commit()
    
    return jsonify({'success': True})
