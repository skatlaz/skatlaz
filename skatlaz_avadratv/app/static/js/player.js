// Video Player Controller
class VideoPlayer {
    constructor(videoElement, options = {}) {
        this.video = videoElement;
        this.options = {
            autoplay: false,
            controls: true,
            volume: 0.5,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.video.volume = this.options.volume;
        
        if (this.options.autoplay) {
            this.video.autoplay = true;
        }
        
        // Create custom controls
        if (!this.options.controls) {
            this.createCustomControls();
        }
        
        // Bind events
        this.video.addEventListener('timeupdate', () => this.updateProgress());
        this.video.addEventListener('ended', () => this.onEnded());
        this.video.addEventListener('play', () => this.onPlay());
        this.video.addEventListener('pause', () => this.onPause());
    }
    
    createCustomControls() {
        const controls = document.createElement('div');
        controls.className = 'custom-controls';
        controls.innerHTML = `
            <button class="play-pause">▶</button>
            <input type="range" class="seek-bar" min="0" max="100" value="0">
            <span class="time-display">0:00 / 0:00</span>
            <input type="range" class="volume-bar" min="0" max="100" value="${this.options.volume * 100}">
            <button class="fullscreen">⛶</button>
        `;
        
        this.video.parentNode.appendChild(controls);
        
        // Bind controls
        controls.querySelector('.play-pause').onclick = () => this.togglePlay();
        controls.querySelector('.seek-bar').oninput = (e) => this.seek(e.target.value);
        controls.querySelector('.volume-bar').oninput = (e) => this.setVolume(e.target.value / 100);
        controls.querySelector('.fullscreen').onclick = () => this.toggleFullscreen();
    }
    
    togglePlay() {
        if (this.video.paused) {
            this.video.play();
        } else {
            this.video.pause();
        }
    }
    
    seek(value) {
        const time = (value / 100) * this.video.duration;
        this.video.currentTime = time;
    }
    
    setVolume(value) {
        this.video.volume = value;
    }
    
    updateProgress() {
        const percent = (this.video.currentTime / this.video.duration) * 100;
        const seekBar = document.querySelector('.seek-bar');
        if (seekBar) seekBar.value = percent;
        
        const timeDisplay = document.querySelector('.time-display');
        if (timeDisplay) {
            timeDisplay.textContent = `${this.formatTime(this.video.currentTime)} / ${this.formatTime(this.video.duration)}`;
        }
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.video.parentNode.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    onPlay() {
        const playBtn = document.querySelector('.play-pause');
        if (playBtn) playBtn.textContent = '⏸';
        
        // Sync with remote control
        this.syncWithRemote({ is_playing: true });
    }
    
    onPause() {
        const playBtn = document.querySelector('.play-pause');
        if (playBtn) playBtn.textContent = '▶';
        
        // Sync with remote control
        this.syncWithRemote({ is_playing: false });
    }
    
    onEnded() {
        this.playNext();
    }
    
    playNext() {
        // Get next video from queue or recommendations
        $.get('/api/player/next', function(data) {
            if (data.video_id) {
                window.location.href = `/watch/${data.video_id}`;
            }
        });
    }
    
    syncWithRemote(state) {
        const token = localStorage.getItem('remote_token');
        if (token) {
            $.post('/api/player/sync', {
                token: token,
                ...state,
                current_time: this.video.currentTime,
                volume: this.video.volume
            });
        }
    }
}

// Initialize player on page load
document.addEventListener('DOMContentLoaded', () => {
    const videoElement = document.getElementById('main-video');
    if (videoElement) {
        const player = new VideoPlayer(videoElement, {
            autoplay: true,
            controls: true
        });
        
        // Track view
        const videoId = videoElement.dataset.videoId;
        if (videoId) {
            $.post('/api/media/view', { video_id: videoId });
        }
    }
});
