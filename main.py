from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

def get_video_info(url):
    """Fetch available video formats and details."""
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        info = get_video_info(url)
        formats = [
            {
                "format_id": f["format_id"],
                "ext": f["ext"],
                "resolution": f.get("resolution"),
                "filesize": f.get("filesize"),
                "url": f["url"]
            } 
            for f in info["formats"] if f.get("url")
        ]
        return jsonify({"title": info["title"], "formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
