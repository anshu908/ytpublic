from pyrogram import Client, filters
from pytube import YouTube
import os

# Bot configuration
API_ID = "14050586"
API_HASH = "42a60d9c657b106370c79bb0a8ac560c"
BOT_TOKEN = "8077840807:AAEjwYQJ3N3vzLnYfaaxJty9yOternFcvXM"

app = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def download_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        video_path = stream.download()
        return video_path, yt.title
    except Exception as e:
        return None, str(e)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a YouTube video link, and I'll download it for you!")

@app.on_message(filters.text & filters.private)
def download(client, message):
    url = message.text.strip()
    message.reply_text("Downloading video, please wait...")
    video_path, title = download_video(url)
    
    if video_path:
        message.reply_video(video=video_path, caption=f"Here is your video: {title}")
        os.remove(video_path)  # Remove the file after sending
    else:
        message.reply_text(f"Failed to download video: {title}")

if __name__ == "__main__":
    app.run()
