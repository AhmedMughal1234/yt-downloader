import streamlit as st
from yt_dlp import YoutubeDL
import os
import base64
from io import BytesIO
from datetime import datetime
import time

# Premium dark theme configuration
st.set_page_config(
    page_title="Premium YouTube Downloader Pro",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Premium CSS styling
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background-color: #0a0a0a;
        color: #f0f0f0;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 12px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #7d58b4 0%, #ad60cb 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Radio buttons */
    .stRadio>div {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 10px;
    }
    .stRadio>div>label>div:first-child {
        background-color: #333 !important;
    }
    
    /* Alerts and info boxes */
    .stAlert {
        background-color: rgba(26, 26, 26, 0.9);
        border-left: 4px solid #6e48aa;
        border-radius: 0 8px 8px 0;
    }
    
    /* Headers */
    h1 {
        color: #9d50bb !important;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5em;
    }
    
    /* Divider */
    hr {
        border-color: #333;
        margin: 2rem 0;
    }
    
    /* Card-like containers */
    .stContainer {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress bar */
    .stProgress>div>div>div {
        background: linear-gradient(90deg, #6e48aa 0%, #9d50bb 100%);
    }
    
    /* Premium badge */
    .premium-badge {
        background: linear-gradient(135deg, #ff8a00 0%, #e52e71 100%);
        color: white;
        padding: 0.2em 0.8em;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 700;
        display: inline-block;
        margin-left: 0.5em;
        vertical-align: middle;
    }
    
    /* Progress info */
    .progress-info {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Premium header section
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("YouTube Downloader Pro")
    st.markdown('<span class="premium-badge">PREMIUM</span>', unsafe_allow_html=True)

st.caption("""
    Download videos in up to 8K resolution or extract high-quality MP3 audio with metadata.
    Professional-grade conversion powered by yt-dlp and FFmpeg.
""")

# URL input with premium styling
with st.container():
    url = st.text_input(
        "Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste any YouTube video URL including playlists and shorts"
    )

# Download options in card
with st.container():
    st.markdown("**Download Options**")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        download_type = st.radio(
            "Download type:",
            ["Video", "MP3 Audio"],
            index=0,
            horizontal=True
        )
    
    with col2:
        if download_type == "Video":
            resolution = st.selectbox(
                "Select video quality:",
                ["720p (Best)", "4K", "1080p", "720p", "480p", "360p", "144p"],
                index=0
            )
        else:
            audio_quality = st.selectbox(
                "Audio quality:",
                ["320kbps (Best)", "256kbps", "192kbps", "128kbps"],
                index=0
            )

# File info section
if url and len(url) > 20:
    with st.container():
        if download_type == "Video":
            size_estimates = {
                "8K": "800MB - 3GB (10-30 min video)",
                "4K": "300MB - 1.5GB (10-30 min video)",
                "1440p": "150MB - 800MB (10-30 min video)",
                "1080p": "80MB - 500MB (10-30 min video)",
                "720p (Best)": "50MB - 300MB (10-30 min video)",
                "720p": "50MB - 300MB (10-30 min video)",
                "480p": "20MB - 150MB (10-30 min video)",
                "360p": "10MB - 80MB (10-30 min video)",
                "144p": "5MB - 30MB (10-30 min video)"
            }
            st.info(f"""
            **Estimated Download Information**
            
            - Quality: {resolution}
            - File size: {size_estimates[resolution]}
            - Format: MP4 (H.264/AAC)
            """)
        else:
            st.info(f"""
            **Estimated Download Information**
            
            - Audio quality: {audio_quality}
            - File size: 3-10MB per minute
            - Format: MP3 (ID3 tags included)
            """)

# Premium download button
if st.button("✨ Process Download", type="primary"):
    if url:
        try:
            # Temporary directory for processing
            temp_dir = "temp_downloads"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Configure premium download options
            if download_type == "Video":
                format_selector = {
                    "720p (Best)": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]",
                    "4K": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=2160]",
                    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]",
                    "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]",
                    "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]",
                    "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=360]",
                    "144p": "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=144]",
                }
                
                ydl_opts = {
                    'format': format_selector[resolution],
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'retries': 10,
                    'fragment_retries': 10,
                    'quiet': True,
                    'no_color': True,
                    'noplaylist': True,
                    'extract_flat': False,
                    'concurrent_fragment_downloads': 4,
                    'socket_timeout': 300,
                    'buffersize': 1024 * 1024 * 16,  # 16MB buffer size
                }
            else:
                quality_map = {
                    "320kbps (Best)": "320",
                    "256kbps": "256",
                    "192kbps": "192",
                    "128kbps": "128"
                }
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': quality_map[audio_quality],
                    }, {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    }],
                    'retries': 10,
                    'quiet': True,
                    'no_color': True,
                    'noplaylist': True,
                    'extract_flat': False,
                    'extractaudio': True,
                    'socket_timeout': 300,
                }

            with st.spinner("Processing premium download..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                timer_text = st.empty()
                start_time = time.time()
                
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        # Get percentage and speed
                        percent = d.get('_percent_str', '0%')
                        percent_float = float(percent.strip('%')) / 100
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        
                        # Update progress bar
                        progress_bar.progress(percent_float)
                        
                        # Calculate elapsed time
                        elapsed = time.time() - start_time
                        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                        
                        # Update status text
                        status_text.markdown(f"""
                        <div class="progress-info">
                            <span>Progress: {percent}</span>
                            <span>Speed: {speed}</span>
                            <span>ETA: {eta}</span>
                            <span>Elapsed: {elapsed_str}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif d['status'] == 'finished':
                        progress_bar.progress(1.0)
                        elapsed = time.time() - start_time
                        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                        status_text.markdown(f"""
                        <div class="progress-info">
                            <span>Processing completed in: {elapsed_str}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                ydl_opts['progress_hooks'] = [progress_hook]
                
                with YoutubeDL(ydl_opts) as ydl:
                    try:
                        # First extract info to check video duration
                        info = ydl.extract_info(url, download=False)
                        duration = info.get('duration', 0)  # in seconds
                        
                        # Show warning if video is longer than 30 minutes
                        if duration > 1800:  # 30 minutes
                            st.warning(f"""
                            ⚠️ Long Video Warning ({(duration//60)} minutes)
                            
                            For best results with long videos:
                            1. Choose a lower resolution (720p or below)
                            2. Ensure stable internet connection
                            3. Don't close the browser during download
                            
                            The download may take several minutes to complete.
                            """)
                        
                        # Start the actual download
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        
                        if download_type == "MP3 Audio":
                            base_filename = os.path.splitext(filename)[0]
                            filename = f"{base_filename}.mp3"
                        
                        # Verify file exists
                        if not os.path.exists(filename):
                            for f in os.listdir(temp_dir):
                                if f.startswith(os.path.splitext(os.path.basename(filename))[0]):
                                    filename = os.path.join(temp_dir, f)
                                    break
                        
                        if not os.path.exists(filename):
                            raise FileNotFoundError("Downloaded file not found")
                        
                        # Get file info
                        file_size = os.path.getsize(filename)
                        size_mb = file_size / (1024 * 1024)
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Show premium download section
                        st.success("""
                        ### ✅ Download Ready
                        
                        Your premium download has been processed successfully.
                        """)
                        
                        # Create a download button that serves the file directly
                        with open(filename, "rb") as file:
                            btn = st.download_button(
                                label=f"⬇️ Download {download_type} ({size_mb:.1f}MB)",
                                data=file,
                                file_name=os.path.basename(filename),
                                mime="video/mp4" if download_type == "Video" else "audio/mp3",
                            )
                        
                        # File details in expandable section
                        with st.expander("📁 Download Details", expanded=True):
                            thumbnail_url = info.get('thumbnail', '')
                            if thumbnail_url:
                                st.image(thumbnail_url, width=300)
                            
                            st.markdown(f"""
                            **File Information**
                            - Name: `{os.path.basename(filename)}`
                            - Type: `{download_type}`
                            - Size: `{size_mb:.2f} MB`
                            - Processed: `{timestamp}`
                            
                            **Video Information**
                            - Title: `{info.get('title', 'N/A')}`
                            - Duration: `{info.get('duration_string', 'N/A')}`
                            - Views: `{info.get('view_count', 'N/A')}`
                            - Uploader: `{info.get('uploader', 'N/A')}`
                            """)
                        
                    except Exception as e:
                        st.error(f"""
                        ### ❌ Processing Error
                        
                        {str(e)}
                        
                        Please try again or contact support if the problem persists.
                        """)
                    finally:
                        # Clean up
                        try:
                            if 'filename' in locals() and os.path.exists(filename):
                                os.remove(filename)
                        except:
                            pass
                        progress_bar.empty()
                        status_text.empty()
                        timer_text.empty()

        except Exception as e:
            st.error(f"""
            ### ❌ Download Failed
            
            {str(e)}
            
            This might be due to:
            - Invalid URL
            - Age-restricted content
            - Regional restrictions
            - Server issues
            - Video too long (try shorter videos or lower quality)
            """)
    else:
        st.warning("Please enter a valid YouTube URL")

# Premium footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9em;">
    <p>© {year} YouTube Downloader Pro | Premium Service</p>
    <p style="font-size: 0.8em;">v2.2.0 | Powered by yt-dlp and FFmpeg</p>
</div>
""".format(year=datetime.now().year), unsafe_allow_html=True)