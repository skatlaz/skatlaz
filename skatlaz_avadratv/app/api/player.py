from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import RemoteSession, Video
import secrets
from datetime import datetime

bp = Blueprint('api_player', __name__, url_prefix='/api/player')

@bp.route('/status', methods=['GET'])
def get_status():
    token = request.args.get('token')
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session or not session.is_active:
        return jsonify({'error': 'Invalid session'}), 404
    
    response = session.to_json()
    
    # Add video details if available
    if session.current_video_id:
        video = Video.query.get(session.current_video_id)
        if video:
            response['current_video'] = {
                'id': video.id,
                'title': video.title,
                'thumbnail': video.thumbnail,
                'duration': video.duration
            }
            response['duration'] = video.duration
    
    return jsonify(response)

@bp.route('/play', methods=['POST'])
def play():
    data = request.get_json()
    token = data.get('token')
    video_id = data.get('video_id')
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    if video_id:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        session.current_video_id = video_id
        session.current_time = 0
    
    session.is_playing = True
    session.last_seen = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'status': 'playing',
        'video_id': session.current_video_id,
        'session': session.to_json()
    })

@bp.route('/pause', methods=['POST'])
def pause():
    data = request.get_json()
    token = data.get('token')
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    session.is_playing = False
    db.session.commit()
    
    return jsonify({'status': 'paused'})

@bp.route('/seek', methods=['POST'])
def seek():
    data = request.get_json()
    token = data.get('token')
    time_position = data.get('time', 0)
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    session.current_time = time_position
    db.session.commit()
    
    return jsonify({'status': 'seeked', 'time': time_position})

@bp.route('/volume', methods=['POST'])
def volume():
    data = request.get_json()
    token = data.get('token')
    volume = data.get('volume', 50)
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    session.volume = max(0, min(100, volume))
    db.session.commit()
    
    return jsonify({'status': 'volume set', 'volume': session.volume})

@bp.route('/queue', methods=['GET', 'POST', 'DELETE'])
def queue_management():
    token = request.args.get('token') or (request.get_json() or {}).get('token')
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    # Initialize queue if not exists
    if not hasattr(session, '_queue'):
        session._queue = []
    
    if request.method == 'GET':
        return jsonify({'queue': session._queue})
    
    elif request.method == 'POST':
        data = request.get_json()
        video_id = data.get('video_id')
        
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        session._queue.append(video_id)
        db.session.commit()
        
        return jsonify({'status': 'added to queue', 'position': len(session._queue) - 1})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        position = data.get('position')
        
        if position is not None and 0 <= position < len(session._queue):
            session._queue.pop(position)
            db.session.commit()
            return jsonify({'status': 'removed from queue'})
        
        return jsonify({'error': 'Invalid position'}), 400

@bp.route('/next', methods=['POST'])
def next_track():
    token = request.get_json().get('token')
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    if not hasattr(session, '_queue') or not session._queue:
        return jsonify({'error': 'Queue is empty'}), 400
    
    next_video_id = session._queue.pop(0)
    session.current_video_id = next_video_id
    session.current_time = 0
    session.is_playing = True
    
    db.session.commit()
    
    return jsonify({
        'status': 'next',
        'video_id': next_video_id
    })

@bp.route('/sessions', methods=['GET'])
@login_required
def list_sessions():
    sessions = RemoteSession.query.filter_by(user_id=current_user.id).all()
    return jsonify([s.to_json() for s in sessions])

@bp.route('/sessions/<token>', methods=['DELETE'])
@login_required
def revoke_session(token):
    session = RemoteSession.query.filter_by(session_token=token, user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    session.is_active = False
    db.session.commit()
    
    return jsonify({'success': True})
