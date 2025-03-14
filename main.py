from pyrogram import Client, filters
import yt_dlp
import os
from flask import Flask
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot configuration
API_ID = "14050586"
API_HASH = "42a60d9c657b106370c79bb0a8ac560c"
BOT_TOKEN = "8077840807:AAEjwYQJ3N3vzLnYfaaxJty9yOternFcvXM"

app = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
web_app = Flask(__name__)

def download_video(url, quality):
    try:
        ydl_opts = {
            'format': f'best[height<={quality}]',  # User selected quality
            'outtmpl': 'video.mp4',
            'noplaylist': True,
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "video.mp4", f"Video Downloaded in {quality}p"
    except Exception as e:
        return None, str(e)

def download_audio(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',  # Best available audio
            'outtmpl': 'audio.mp3',
            'noplaylist': True,
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "audio.mp3", "🎵 Enjoy Your Audio Track!"
    except Exception as e:
        return None, str(e)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a YouTube video link, and I'll download it for you!")

@app.on_message(filters.text & filters.private)
def ask_quality(client, message):
    url = message.text.strip()
    
    buttons = [
        [InlineKeyboardButton("🔹 240p (Fastest)", callback_data=f"quality_240_{url}")],
        [InlineKeyboardButton("🔹 360p (Good Quality)", callback_data=f"quality_360_{url}")],
        [InlineKeyboardButton("🔹 480p (Better Quality)", callback_data=f"quality_480_{url}")],
        [InlineKeyboardButton("🎵 Audio Only", callback_data=f"audio_{url}")]
    ]

    message.reply_text("Select the quality you want:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
def handle_callback(client, callback_query):
    data = callback_query.data.split("_")
    
    if data[0] == "quality":
        quality = data[1]
        url = "_".join(data[2:])
        callback_query.message.edit_text(f"Downloading video in {quality}p... Please wait ⏳")
        
        video_path, title = download_video(url, quality)
        
        if video_path:
            callback_query.message.reply_video(video=video_path, caption=f"Here is your {quality}p video! 🎥")
            os.remove(video_path)
        else:
            callback_query.message.reply_text(f"Failed to download video: {title}")

    elif data[0] == "audio":
        url = "_".join(data[1:])
        callback_query.message.edit_text("Downloading audio... 🎧")
        
        audio_path, title = download_audio(url)
        
        if audio_path:
            callback_query.message.reply_audio(audio=audio_path, caption=title)
            os.remove(audio_path)
        else:
            callback_query.message.reply_text(f"Failed to download audio: {title}")

@web_app.route("/")
def home():
    return "YouTube Downloader Bot is running!"

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: web_app.run(host="0.0.0.0", port=8000)).start()
    app.run()
