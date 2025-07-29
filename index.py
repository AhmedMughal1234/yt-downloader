import os
import sys
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from tqdm import tqdm

def get_video_info(url):
    """Fetch video info and available formats."""
    ydl_opts = {'quiet': True, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except DownloadError as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

def choose_format(formats, preferred_list):
    """Choose the best format from preferred resolutions."""
    for res in preferred_list:
        for f in formats:
            if f.get('height') == res and f.get('ext') == 'mp4' and f.get('acodec') != 'none':
                return f
    return None

def list_available_qualities(formats):
    """List available video qualities."""
    qualities = []
    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
            if f.get('height') not in qualities:
                qualities.append(f.get('height'))
    return sorted(qualities, reverse=True)

def download_with_progress(url, format_id, output_path):
    """Download video with progress bar."""
    class TqdmHook:
        def __init__(self):
            self.pbar = None
        def __call__(self, d):
            if d['status'] == 'downloading':
                if self.pbar is None:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    self.pbar = tqdm(total=total, unit='B', unit_scale=True, desc='Downloading')
                downloaded = d.get('downloaded_bytes', 0)
                self.pbar.n = downloaded
                self.pbar.refresh()
            elif d['status'] == 'finished':
                if self.pbar:
                    self.pbar.n = self.pbar.total
                    self.pbar.close()
                    print('Download completed!')
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [TqdmHook()],
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    return True

def main():
    print("YouTube Video Downloader (yt-dlp)")
    url = input("Enter YouTube video URL: ").strip()
    if not url:
        print("No URL entered. Exiting.")
        sys.exit(1)
    info = get_video_info(url)
    if not info:
        print("Failed to retrieve video info. Exiting.")
        sys.exit(1)
    formats = info.get('formats', [])
    if not formats:
        print("No downloadable formats found.")
        sys.exit(1)
    qualities = list_available_qualities(formats)
    if not qualities:
        print("No suitable video qualities found.")
        sys.exit(1)
    print("\nAvailable qualities:")
    for i, q in enumerate(qualities):
        print(f"  {i+1}. {q}p")
    print("  0. Best available (default: 1080p > 720p > 360p)")
    try:
        choice = int(input("Select quality (enter number): "))
    except ValueError:
        choice = 0
    preferred = [1080, 720, 360]
    if choice == 0:
        fmt = choose_format(formats, preferred)
    elif 1 <= choice <= len(qualities):
        fmt = choose_format(formats, [qualities[choice-1]])
    else:
        print("Invalid choice. Using default.")
        fmt = choose_format(formats, preferred)
    if not fmt:
        print("Requested quality not available. Trying best available...")
        fmt = choose_format(formats, qualities)
    if not fmt:
        print("No suitable format found. Exiting.")
        sys.exit(1)
    format_id = fmt['format_id']
    downloads_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    print(f"\nDownloading: {info.get('title')} [{fmt.get('height')}p]")
    success = download_with_progress(url, format_id, downloads_dir)
    if success:
        print(f"\nSaved to: {downloads_dir}")
    else:
        print("Download failed.")

if __name__ == "__main__":
    main()
