from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db, thumbnails
from app.models import User, Channel, Video
from app.forms import ChannelEditForm
import os

bp = Blueprint('channel', __name__)

@bp.route('/@<username>')
def view(username):
    user = User.query.filter_by(username=username).first_or_404()
    channel = user.channel
    
    page = request.args.get('page', 1, type=int)
    videos = Video.query.filter_by(user_id=user.id, is_published=True)\
        .order_by(Video.created_at.desc())\
        .paginate(page=page, per_page=12)
    
    return render_template('channel.html', user=user, channel=channel, videos=videos)

@bp.route('/channel/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = ChannelEditForm()
    channel = current_user.channel
    
    if form.validate_on_submit():
        channel.name = form.name.data
        channel.description = form.description.data
        channel.custom_url = form.custom_url.data
        
        if form.banner.data:
            banner_file = form.banner.data
            banner_filename = f"banner_{current_user.id}.{banner_file.filename.split('.')[-1]}"
            banner_file.save(os.path.join(current_app.config['UPLOADED_THUMBNAILS_DEST'], banner_filename))
            channel.banner = banner_filename
        
        db.session.commit()
        flash('Channel updated successfully!', 'success')
        return redirect(url_for('channel.view', username=current_user.username))
    
    form.name.data = channel.name
    form.description.data = channel.description
    form.custom_url.data = channel.custom_url
    
    return render_template('edit_channel.html', form=form, channel=channel)

@bp.route('/channel/subscribe/<int:channel_id>', methods=['POST'])
@login_required
def subscribe(channel_id):
    from app.models import Subscription
    
    channel = Channel.query.get_or_404(channel_id)
    
    if channel.user_id == current_user.id:
        return jsonify({'error': 'Cannot subscribe to your own channel'}), 400
    
    subscription = Subscription.query.filter_by(
        user_id=current_user.id,
        channel_id=channel_id
    ).first()
    
    if subscription:
        db.session.delete(subscription)
        channel.subscribers -= 1
        subscribed = False
    else:
        subscription = Subscription(user_id=current_user.id, channel_id=channel_id)
        db.session.add(subscription)
        channel.subscribers += 1
        subscribed = True
    
    db.session.commit()
    
    return jsonify({
        'subscribed': subscribed,
        'subscribers': channel.subscribers
    })
