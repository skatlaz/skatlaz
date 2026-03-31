from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.models import Video, User, Channel
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    
    # Get trending videos (most viewed in last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    trending = Video.query.filter(
        Video.is_published == True,
        Video.created_at >= week_ago
    ).order_by(Video.views.desc()).limit(12).all()
    
    # Latest uploads
    latest = Video.query.filter_by(is_published=True)\
        .order_by(Video.created_at.desc())\
        .paginate(page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    
    # Popular channels
    popular_channels = Channel.query.order_by(Channel.subscribers.desc()).limit(10).all()
    
    return render_template('index.html', 
                         trending=trending, 
                         latest=latest,
                         popular_channels=popular_channels)

@bp.route('/trending')
def trending():
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    videos = Video.query.filter(
        Video.is_published == True,
        Video.created_at >= week_ago
    ).order_by(Video.views.desc()).paginate(
        page=request.args.get('page', 1, type=int),
        per_page=current_app.config['ITEMS_PER_PAGE']
    )
    
    return render_template('trending.html', videos=videos)

@bp.route('/feed')
@login_required
def feed():
    # Get videos from subscribed channels
    from app.models import Subscription
    
    subscribed_channels = Subscription.query.filter_by(user_id=current_user.id).all()
    channel_ids = [sub.channel_id for sub in subscribed_channels]
    
    videos = Video.query.filter(
        Video.is_published == True,
        Video.channel_id.in_(channel_ids)
    ).order_by(Video.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int),
        per_page=current_app.config['ITEMS_PER_PAGE']
    )
    
    return render_template('feed.html', videos=videos)

@bp.route('/about')
def about():
    return render_template('about.html')
