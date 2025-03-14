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

# ✅ URL ko session storage me store karenge
session_data = {}

QUALITY_OPTIONS = {
    "240p": "q1",
    "360p": "q2",
    "480p": "q3",
    "audio": "a1"
}

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a YouTube video link, and I'll download it for you!")

@app.on_message(filters.text & filters.private)
def ask_quality(client, message):
    url = message.text.strip()
    session_data[message.chat.id] = url  # ✅ URL Store kiya

    buttons = [
        [InlineKeyboardButton("🔹 240p", callback_data="q1")],
        [InlineKeyboardButton("🔹 360p", callback_data="q2")],
        [InlineKeyboardButton("🔹 480p", callback_data="q3")],
        [InlineKeyboardButton("🎵 Audio", callback_data="a1")]
    ]

    message.reply_text("Select the quality you want:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
def handle_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    quality_map = {"q1": "240p", "q2": "360p", "q3": "480p", "a1": "audio"}
    selected_quality = quality_map[callback_query.data]
    
    url = session_data.get(chat_id)  # ✅ Stored URL retrieve kiya

    callback_query.message.edit_text(f"Downloading {selected_quality}... Please wait ⏳")

    if selected_quality == "audio":
        file_path, title = download_audio(url)
        callback_query.message.reply_audio(audio=file_path, caption=title)
        os.remove(file_path)
    else:
        file_path, title = download_video(url, selected_quality)
        callback_query.message.reply_video(video=file_path, caption=title)
        os.remove(file_path)

# ✅ Function to download YouTube videos
def download_video(url, quality):
    ydl_opts = {
        'format': f'best[height<={quality}]',
        'outtmpl': 'video.mp4',
        'noplaylist': True,
        'quiet': True,
        'cookies': 'cookies.txt'  # ✅ Fix ke liye cookies use kiya
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "video.mp4", f"Downloaded {quality} video"

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.mp3',
        'noplaylist': True,
        'quiet': True,
        'cookies': 'cookies.txt'  # ✅ Fix ke liye cookies use kiya
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "audio.mp3", "Downloaded Audio"

@web_app.route("/")
def home():
    return "YouTube Downloader Bot is running!"

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: web_app.run(host="0.0.0.0", port=8000)).start()
    app.run()
