// Main application JavaScript
$(document).ready(function() {
    // Infinite scroll for video feed
    let loading = false;
    let page = 1;
    
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
            if (!loading) {
                loading = true;
                loadMoreVideos();
            }
        }
    });
    
    function loadMoreVideos() {
        page++;
        const url = window.location.pathname;
        
        $.get(`${url}?page=${page}`, function(data) {
            const videos = $(data).find('.video-card');
            if (videos.length > 0) {
                $('#videos-container').append(videos);
                loading = false;
            }
        });
    }
    
    // Search autocomplete
    $('#search-input').on('input', debounce(function() {
        const query = $(this).val();
        if (query.length < 2) return;
        
        $.get('/api/search/suggestions', { q: query }, function(suggestions) {
            const html = suggestions.map(s => `
                <div class="suggestion-item" data-url="${s.url}">
                    <i class="fas ${s.type === 'video' ? 'fa-video' : 'fa-users'}"></i>
                    ${s.title}
                </div>
            `).join('');
            
            $('#search-suggestions').html(html).show();
        });
    }, 300));
    
    // Click outside to close suggestions
    $(document).click(function(e) {
        if (!$(e.target).closest('#search-form').length) {
            $('#search-suggestions').hide();
        }
    });
    
    // Subscribe button
    $('.subscribe-btn').click(function() {
        const channelId = $(this).data('channel-id');
        const btn = $(this);
        
        $.post(`/channel/subscribe/${channelId}`, function(response) {
            if (response.subscribed) {
                btn.text('Subscribed').removeClass('btn-outline-primary').addClass('btn-primary');
            } else {
                btn.text('Subscribe').removeClass('btn-primary').addClass('btn-outline-primary');
            }
            btn.find('.subscriber-count').text(response.subscribers);
        });
    });
    
    // Like/Dislike animation
    $('.like-btn, .dislike-btn').click(function() {
        const btn = $(this);
        btn.addClass('animate__animated animate__heartBeat');
        setTimeout(() => btn.removeClass('animate__animated animate__heartBeat'), 500);
    });
    
    // Share modal
    $('#share-btn').click(function() {
        const url = window.location.href;
        const shareText = `Check out this video on Skatzla AvadraTV! ${url}`;
        
        // Copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copied to clipboard!');
        });
    });
    
    // Video upload preview
    $('#video-file').on('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#video-preview').attr('src', e.target.result).show();
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Thumbnail upload preview
    $('#thumbnail-file').on('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#thumbnail-preview').attr('src', e.target.result).show();
            };
            reader.readAsDataURL(file);
        }
    });
});

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format numbers (views, subscribers)
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Lazy load images
document.addEventListener("DOMContentLoaded", function() {
    let lazyImages = [].slice.call(document.querySelectorAll("img.lazy"));
    
    if ("IntersectionObserver" in window) {
        let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    let lazyImage = entry.target;
                    lazyImage.src = lazyImage.dataset.src;
                    lazyImage.classList.remove("lazy");
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });
        
        lazyImages.forEach(function(lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    }
});
