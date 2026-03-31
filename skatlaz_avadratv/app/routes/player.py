from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import RemoteSession, Video
import secrets
from datetime import datetime

bp = Blueprint('player', __name__)

@bp.route('/remote')
@login_required
def remote_control():
    sessions = RemoteSession.query.filter_by(user_id=current_user.id).all()
    return render_template('player_control.html', sessions=sessions)

@bp.route('/api/player/create_session', methods=['POST'])
@login_required
def create_session():
    data = request.get_json() or {}
    device_name = data.get('device_name', 'Unknown Device')
    
    token = secrets.token_urlsafe(32)
    session = RemoteSession(
        session_token=token,
        device_name=device_name,
        user_id=current_user.id,
        is_active=True
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'token': token,
        'session': session.to_json()
    })

@bp.route('/api/player/sync', methods=['POST'])
def sync_player():
    """Sync player state from client"""
    data = request.get_json()
    token = data.get('token')
    
    session = RemoteSession.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    session.is_playing = data.get('is_playing', session.is_playing)
    session.current_time = data.get('current_time', session.current_time)
    session.volume = data.get('volume', session.volume)
    session.last_seen = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})
