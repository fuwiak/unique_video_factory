import yt_dlp

def download_instagram_reel(url):
    ydl_opts = {
        'outtmpl': 'reel_video.mp4',  # output filename
        'quiet': True,  # suppress verbose output for test
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download succeeded.")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    reel_url = "https://www.instagram.com/reels/DNhNjlYsQR4/"
    download_instagram_reel(reel_url)
