import os
import uuid
import hashlib
from PIL import Image
import moviepy.editor as mp
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import subprocess
import logging

logger = logging.getLogger(__name__)

def generate_thumbnail(video_path, output_path, time_seconds=5):
    """Generate thumbnail from video at specific time"""
    try:
        video = mp.VideoFileClip(video_path)
        frame = video.get_frame(time_seconds)
        
        # Convert to PIL Image
        img = Image.fromarray(frame)
        
        # Resize to standard thumbnail size
        img.thumbnail((1280, 720), Image.Resampling.LANCZOS)
        img.save(output_path, 'JPEG', quality=85)
        
        video.close()
        return True
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return False

def get_video_duration(video_path):
    """Get video duration in seconds"""
    try:
        video = mp.VideoFileClip(video_path)
        duration = video.duration
        video.close()
        return int(duration)
    except Exception as e:
        logger.error(f"Error getting video duration: {e}")
        return 0

def get_audio_duration(audio_path):
    """Get audio duration in seconds"""
    try:
        if audio_path.endswith('.mp3'):
            audio = MP3(audio_path)
            return int(audio.info.length)
        elif audio_path.endswith('.m4a'):
            audio = MP4(audio_path)
            return int(audio.info.length)
        else:
            # Use ffprobe for other formats
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                   '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return int(float(result.stdout))
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return 0

def generate_unique_filename(original_filename):
    """Generate unique filename for uploads"""
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def sanitize_filename(filename):
    """Remove unsafe characters from filename"""
    return "".join(c for c in filename if c.isalnum() or c in '.-_').rstrip()

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS"""
    if not seconds:
        return "0:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def truncate_text(text, max_length=100):
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def extract_hashtags(text):
    """Extract hashtags from text"""
    import re
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def validate_video_file(file):
    """Validate video file type and size"""
    allowed_types = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska']
    if file.mimetype not in allowed_types:
        return False, "Invalid video format"
    
    if file.content_length > 16 * 1024 * 1024 * 1024:  # 16GB
        return False, "File too large (max 16GB)"
    
    return True, "Valid"
