from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()
    
    # Create channel
    from app.models import Channel
    channel = Channel(
        user_id=user.id,
        name=user.username,
        custom_url=user.username.lower()
    )
    db.session.add(channel)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'channel': {
            'id': channel.id,
            'name': channel.name,
            'custom_url': channel.custom_url
        }
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'avatar': current_user.avatar,
        'channel': {
            'id': current_user.channel.id,
            'name': current_user.channel.name,
            'subscribers': current_user.channel.subscribers
        }
    })
