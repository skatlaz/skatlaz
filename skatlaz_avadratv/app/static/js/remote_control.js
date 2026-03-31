// Remote Control Manager
class RemoteControlManager {
    constructor() {
        this.token = localStorage.getItem('remote_token');
        this.session = null;
        this.pollingInterval = null;
        this.init();
    }
    
    init() {
        if (this.token) {
            this.connect(this.token);
        }
        
        // Listen for token input
        $('#connect-token').on('submit', (e) => {
            e.preventDefault();
            const token = $('#token-input').val();
            this.connect(token);
        });
    }
    
    connect(token) {
        $.get(`/api/player/status?token=${token}`, (session) => {
            this.token = token;
            this.session = session;
            localStorage.setItem('remote_token', token);
            this.startPolling();
            this.updateUI();
            $('#connection-status').html('<span class="text-success">✓ Connected</span>');
        }).fail(() => {
            $('#connection-status').html('<span class="text-danger">✗ Connection failed</span>');
        });
    }
    
    startPolling() {
        if (this.pollingInterval) clearInterval(this.pollingInterval);
        
        this.pollingInterval = setInterval(() => {
            $.get(`/api/player/status?token=${this.token}`, (session) => {
                this.session = session;
                this.updateUI();
            });
        }, 1000);
    }
    
    updateUI() {
        if (!this.session) return;
        
        // Update current video info
        if (this.session.current_video) {
            $('#current-title').text(this.session.current_video.title);
            $('#current-thumbnail').attr('src', `/static/uploads/thumbnails/${this.session.current_video.thumbnail}`);
            
            // Update progress
            const progress = (this.session.current_time / this.session.duration) * 100;
            $('#progress-bar').css('width', `${progress}%`);
            $('#current-time').text(this.formatTime(this.session.current_time));
            $('#duration').text(this.formatTime(this.session.duration));
        }
        
        // Update play/pause button
        const playIcon = this.session.is_playing ? '⏸' : '▶';
        $('#play-pause-btn').text(playIcon);
        
        // Update volume
        $('#volume-slider').val(this.session.volume);
        $('#volume-value').text(`${this.session.volume}%`);
        
        // Update device status
        $('.device-status').removeClass('active inactive');
        $('.device-status').addClass(this.session.is_active ? 'active' : 'inactive');
    }
    
    sendCommand(command, data = {}) {
        data.token = this.token;
        $.post(`/api/player/${command}`, data, (response) => {
            if (response.status === 'playing') {
                this.session.is_playing = true;
            } else if (response.status === 'paused') {
                this.session.is_playing = false;
            }
            this.updateUI();
        });
    }
    
    play() {
        this.sendCommand('play');
    }
    
    pause() {
        this.sendCommand('pause');
    }
    
    seek(time) {
        this.sendCommand('seek', { time: time });
    }
    
    setVolume(volume) {
        this.sendCommand('volume', { volume: volume });
    }
    
    next() {
        this.sendCommand('next');
    }
    
    formatTime(seconds) {
        if (!seconds) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    disconnect() {
        clearInterval(this.pollingInterval);
        localStorage.removeItem('remote_token');
        this.token = null;
        this.session = null;
        $('#connection-status').html('<span class="text-muted">Not connected</span>');
    }
}

// Initialize remote control on page load
$(document).ready(() => {
    const remote = new RemoteControlManager();
    
    // Bind control buttons
    $('#play-pause-btn').click(() => remote.sendCommand('play_pause'));
    $('#next-btn').click(() => remote.sendCommand('next'));
    $('#prev-btn').click(() => remote.sendCommand('prev'));
    $('#volume-slider').on('input', (e) => remote.setVolume(e.target.value));
    $('#seek-bar').on('input', (e) => remote.seek(e.target.value));
    $('#disconnect-btn').click(() => remote.disconnect());
});
