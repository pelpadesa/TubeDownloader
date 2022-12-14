from tkinter import StringVar
from urllib.parse import urlparse, parse_qs
from contextlib import suppress
from yt_dlp import YoutubeDL
from os.path import isfile
import json

def get_yt_id(url, ignore_playlist=True):
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[1]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]

class VideoHandler:
    def __init__(self) -> None:
        self.VideoTitle = StringVar(value="No Video Grabbed")
        self.VideoURL = StringVar(value="")
        self.VideoThumbnailURL = StringVar(value="")
        self.VideoAuthor = StringVar(value="")
        self.VideoID = StringVar(value="")
        
        self.Progress = 0
        self.Status = ""

    def GrabVideo(self):
        video_url = self.VideoURL.get()
        with YoutubeDL() as ytdl:
            videoInfo = ytdl.extract_info(video_url, download=False)
            jsonData = ytdl.sanitize_info(videoInfo)
            with open("./bin/videoData.json", "w+") as videoDataFile:
                videoDataFile.write(json.dumps(jsonData, indent=4))
        
        self.VideoThumbnailURL.set(jsonData.get("thumbnail"))
        self.VideoTitle.set(jsonData.get("title"))
        self.VideoAuthor.set(jsonData.get("uploader"))
        self.VideoID.set(jsonData.get("id"))
    def DownloadVideo(self, format_id, path):
        # Start download
        # def update() -> self.progress, etc
        # outside download thread, poll progress, relay to progress bar, status messages, etc
        videoExt = path.split(".")[-1].lower() # MP3/MP4
        with open("./bin/videoData.json", "r") as videoDataFile:
            videoData = json.loads(videoDataFile.read())

        ydl_opts = {
            'outtmpl': f'{path}',
            'noplaylist': 'true',
            'quiet': 'true',
            'progress_hooks': [self.UpdateProgress],
            'merge_output_format': videoExt,
            'final_ext': videoExt,
            'ffmpeg_location': "./bin"
        }
        if videoExt == "mp3":
            ydl_opts["format"] = f"bestaudio[ext=m4a]"
            ydl_opts["allow_multiple_audio_streams"] = True
            ydl_opts["postprocessors"] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        else: 
            videoResolution = None
            for format in videoData.get("formats"):
                if format.get("format_id") == format_id:
                    videoResolution = format.get("resolution").split("x")
                    videoWidth = videoResolution[0]
                    videoHeight = videoResolution[1]
                    break
            if videoResolution is None:
                return
            
            ydl_opts["format"] = f'bestvideo[height<={videoHeight}][ext=mp4]+bestaudio[ext=m4a] / bestvideo[width<={videoWidth}][ext=mp4]+bestaudio[ext=m4a]'
        
        with YoutubeDL(ydl_opts) as ydl_download:
            ydl_download.download(self.VideoURL.get())

    def UpdateProgress(self, info):
        if info.get("status") == "finished":
            fileName = info.get("filename")
            if isfile(fileName) and isfile(fileName.replace(".mp3", ".m4a")):
                self.Status = "Converting M4A to MP3..."
                self.Progress = 0.9
            return
        elif info.get("status") == "downloading":
            total_size = info.get("total_bytes")
            downloaded_size = info.get("downloaded_bytes")
            # total_size / 100 = 1%
            # downloaded_size / 1% = % Progress
            self.Progress = downloaded_size / (total_size / 100) / 100
            self.Status = f'Downloading at ' + info.get("_speed_str").replace("\u001b[0;32m", "").replace("\u001b[0m", "")
        with open("./bin/videoData.json", "w+") as videoDataFile:
            videoDataFile.write(json.dumps(info, indent=4))



