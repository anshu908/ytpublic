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
            'format': f'best[height<={quality}]',  
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
            'format': 'bestaudio/best',
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

    # ✅ Callback data ko short kiya
    buttons = [
        [InlineKeyboardButton("🔹 240p (Fast)", callback_data=f"q_240|{url}")],
        [InlineKeyboardButton("🔹 360p (Good)", callback_data=f"q_360|{url}")],
        [InlineKeyboardButton("🔹 480p (Better)", callback_data=f"q_480|{url}")],
        [InlineKeyboardButton("🎵 Audio Only", callback_data=f"a|{url}")]
    ]

    message.reply_text("Select the quality you want:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
def handle_callback(client, callback_query):
    data = callback_query.data.split("|")

    if data[0].startswith("q_"):
        quality = data[0][2:]  # Extract quality (240, 360, 480)
        url = data[1]
        callback_query.message.edit_text(f"Downloading {quality}p video... Please wait ⏳")
        
        video_path, title = download_video(url, quality)
        
        if video_path:
            callback_query.message.reply_video(video=video_path, caption=f"Here is your {quality}p video! 🎥")
            os.remove(video_path)
        else:
            callback_query.message.reply_text(f"Failed to download video: {title}")

    elif data[0] == "a":
        url = data[1]
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
