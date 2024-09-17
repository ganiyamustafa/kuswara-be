import yt_dlp as youtube_dl

def download_youtube_video(url):
  ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'extract_flat': True,  # Fetch video metadata without downloading
    'force_generic_extractor': True
  }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      audio_url = info.get('url')
      # duration = info.get('duration', 0)
      # print("Audio URL:", audio_url, "duration:", duration)
      return audio_url

# Main function
def youtube_to_mp3(url):
  return download_youtube_video(url)