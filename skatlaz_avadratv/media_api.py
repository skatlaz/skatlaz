import json
import requests
from flask import Flask, jsonify, request, session
from flask_cors import CORS

class MediaPlayerAPI:
    """
    Remote media player API for controlling video/audio playback
    """
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.player_states = {}  # Store player states in memory
        if app:
            self.init_app(app, db)
    
    def init_app(self, app, db):
        self.app = app
        self.db = db
        self.register_routes()
    
    def register_routes(self):
        """Register API routes for remote control"""
        
        @self.app.route('/api/player/status', methods=['GET'])
        def get_player_status():
            """Get current player status"""
            token = request.args.get('token')
            if not token:
                return jsonify({'error': 'No session token'}), 400
            
            from app.models import RemoteSession
            session_obj = RemoteSession.query.filter_by(session_token=token).first()
            
            if not session_obj or not session_obj.is_active:
                return jsonify({'error': 'Invalid or inactive session'}), 404
            
            return jsonify(session_obj.to_json())
        
        @self.app.route('/api/player/play', methods=['POST'])
        def player_play():
            """Start playback"""
            data = request.json
            token = data.get('token')
            video_id = data.get('video_id')
            
            from app.models import RemoteSession, Video
            
            session_obj = RemoteSession.query.filter_by(session_token=token).first()
            if not session_obj:
                return jsonify({'error': 'Invalid session'}), 404
            
            if video_id:
                video = Video.query.get(video_id)
                if not video:
                    return jsonify({'error': 'Video not found'}), 404
                session_obj.current_video_id = video_id
                session_obj.current_time = 0
            
            session_obj.is_playing = True
            session_obj.last_seen = datetime.utcnow()
            self.db.session.commit()
            
            return jsonify({'status': 'playing', 'video': video_id})
        
        @self.app.route('/api/player/pause', methods=['POST'])
        def player_pause():
            """Pause playback"""
            data = request.json
            token = data.get('token')
            
            from app.models import RemoteSession
            
            session_obj = RemoteSession.query.filter_by(session_token=token).first()
            if not session_obj:
                return jsonify({'error': 'Invalid session'}), 404
            
            session_obj.is_playing = False
            self.db.session.commit()
            
            return jsonify({'status': 'paused'})
        
        @self.app.route('/api/player/seek', methods=['POST'])
        def player_seek():
            """Seek to specific time"""
            data = request.json
            token = data.get('token')
            time_position = data.get('time', 0)
            
            from app.models import RemoteSession
            
            session_obj = RemoteSession.query.filter_by(session_token=token).first()
            if not session_obj:
                return jsonify({'error': 'Invalid session'}), 404
            
            session_obj.current_time = time_position
            self.db.session.commit()
            
            return jsonify({'status': 'seeked', 'time': time_position})
        
        @self.app.route('/api/player/volume', methods=['POST'])
        def player_volume():
            """Set volume"""
            data = request.json
            token = data.get('token')
            volume = data.get('volume', 50)
            
            from app.models import RemoteSession
            
            session_obj = RemoteSession.query.filter_by(session_token=token).first()
            if not session_obj:
                return jsonify({'error': 'Invalid session'}), 404
            
            session_obj.volume = max(0, min(100, volume))
            self.db.session.commit()
            
            return jsonify({'status': 'volume set', 'volume': session_obj.volume})
        
        @self.app.route('/api/player/queue', methods=['GET', 'POST', 'DELETE'])
        def player_queue():
            """Manage playback queue"""
            token = request.args.get('token') or request.json.get('token')
            
            from app.models import RemoteSession
            
            session_obj = RemoteSession.query.filter_by(session_token=token).first()
            if not session_obj:
                return jsonify({'error': 'Invalid session'}), 404
            
            # Store queue in session object (you might want to create a separate model)
            if request.method == 'GET':
                queue = session_obj.queue if hasattr(session_obj, 'queue') else []
                return jsonify({'queue': queue})
            
            elif request.method == 'POST':
                video_id = request.json.get('video_id')
                if not hasattr(session_obj, 'queue'):
                    session_obj.queue = []
                session_obj.queue.append(video_id)
                self.db.session.commit()
                return jsonify({'status': 'added to queue'})
            
            elif request.method == 'DELETE':
                position = request.json.get('position')
                if hasattr(session_obj, 'queue') and position < len(session_obj.queue):
                    session_obj.queue.pop(position)
                    self.db.session.commit()
                return jsonify({'status': 'removed from queue'})
    
    def create_session(self, user_id=None, device_name=None):
        """Create a new remote control session"""
        import secrets
        from app.models import RemoteSession
        
        token = secrets.token_urlsafe(32)
        session_obj = RemoteSession(
            session_token=token,
            user_id=user_id,
            device_name=device_name,
            is_active=True
        )
        self.db.session.add(session_obj)
        self.db.session.commit()
        
        return token
    
    def broadcast_state(self, token, state):
        """Broadcast player state to connected clients (WebSocket would be better)"""
        # For now, just update the session
        from app.models import RemoteSession
        session_obj = RemoteSession.query.filter_by(session_token=token).first()
        if session_obj:
            session_obj.is_playing = state.get('is_playing', session_obj.is_playing)
            session_obj.current_time = state.get('current_time', session_obj.current_time)
            session_obj.volume = state.get('volume', session_obj.volume)
            self.db.session.commit()
