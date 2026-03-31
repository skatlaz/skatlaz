from flask import Blueprint, request, jsonify
from app.models import Video, User, Channel
from sqlalchemy import or_, func
import re

bp = Blueprint('api_search', __name__, url_prefix='/api/search')

@bp.route('', methods=['GET'])
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')  # all, video, channel
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'results': [], 'total': 0})
    
    results = {}
    
    if search_type in ['all', 'video']:
        video_results = search_videos(query, page, limit)
        results['videos'] = video_results
    
    if search_type in ['all', 'channel']:
        channel_results = search_channels(query, page, limit)
        results['channels'] = channel_results
    
    return jsonify(results)

def search_videos(query, page, limit):
    # Split query into words for better matching
    words = query.lower().split()
    
    # Build search conditions
    conditions = []
    for word in words:
        conditions.append(Video.title.ilike(f'%{word}%'))
        conditions.append(Video.description.ilike(f'%{word}%'))
        conditions.append(Video.hashtags.ilike(f'%{word}%'))
    
    # Search with relevance scoring
    videos = Video.query.filter(
        Video.is_published == True,
        or_(*conditions)
    ).all()
    
    # Calculate relevance score
    scored_videos = []
    for video in videos:
        score = 0
        title_lower = video.title.lower()
        desc_lower = video.description.lower()
        
        for word in words:
            # Title matches have higher weight
            if word in title_lower:
                score += 10
            # Description matches
            if word in desc_lower:
                score += 3
            # Hashtag matches
            if video.hashtags and word in video.hashtags.lower():
                score += 5
        
        # Boost by views and likes
        score += min(video.views / 1000, 10)
        score += min(video.likes / 100, 5)
        
        scored_videos.append((video, score))
    
    # Sort by score
    scored_videos.sort(key=lambda x: x[1], reverse=True)
    
    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated = scored_videos[start:end]
    
    return {
        'items': [{
            'id': v.id,
            'title': v.title,
            'thumbnail': v.thumbnail,
            'duration': v.duration,
            'views': v.views,
            'username': v.uploader.username,
            'score': score
        } for v, score in paginated],
        'total': len(scored_videos),
        'page': page,
        'limit': limit
    }

def search_channels(query, page, limit):
    words = query.lower().split()
    
    conditions = []
    for word in words:
        conditions.append(Channel.name.ilike(f'%{word}%'))
        conditions.append(Channel.description.ilike(f'%{word}%'))
    
    channels = Channel.query.filter(or_(*conditions)).all()
    
    # Score channels
    scored_channels = []
    for channel in channels:
        score = 0
        name_lower = channel.name.lower()
        
        for word in words:
            if word in name_lower:
                score += 10
            if channel.description and word in channel.description.lower():
                score += 3
        
        # Boost by subscribers
        score += min(channel.subscribers / 1000, 20)
        
        scored_channels.append((channel, score))
    
    scored_channels.sort(key=lambda x: x[1], reverse=True)
    
    start = (page - 1) * limit
    end = start + limit
    paginated = scored_channels[start:end]
    
    return {
        'items': [{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'custom_url': c.custom_url,
            'subscribers': c.subscribers,
            'banner': c.banner,
            'username': c.owner.username,
            'score': score
        } for c, score in paginated],
        'total': len(scored_channels),
        'page': page,
        'limit': limit
    }

@bp.route('/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    
    # Get video title suggestions
    videos = Video.query.filter(
        Video.is_published == True,
        Video.title.ilike(f'%{query}%')
    ).limit(5).all()
    
    # Get channel suggestions
    channels = Channel.query.filter(
        Channel.name.ilike(f'%{query}%')
    ).limit(5).all()
    
    suggestions = []
    
    for video in videos:
        suggestions.append({
            'type': 'video',
            'title': video.title,
            'url': f'/watch/{video.id}'
        })
    
    for channel in channels:
        suggestions.append({
            'type': 'channel',
            'title': channel.name,
            'url': f'/@{channel.custom_url}'
        })
    
    return jsonify(suggestions[:10])
