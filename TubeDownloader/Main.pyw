import customtkinter
from PIL import Image
from requests import get
from bin.custom_models import custom_CTkComboBox
from bin.video_handling import VideoHandler
from tkinter import filedialog
from threading import Thread
import time
import json
import sys
import os

sys.stderr = open('./bin/logs/err.log', 'w+')
sys.stdout = open('./bin/logs/out.log', 'w+')

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class MainWindow(customtkinter.CTk):
    def __init__(self, geometry, title):
        super().__init__()

        self.geometry(geometry)
        self.title(title)
        self.resizable(width = False, height = False)
        self.iconbitmap("./td.ico")
        self.handler = VideoHandler()
        self.VideoQualities, self.AudioQualities = [], []

        # Main Frame
        frame_1 = customtkinter.CTkFrame(master = self)
        frame_1.pack(pady = (10,0), padx = 10, fill = "both", expand = True, anchor="n")
        self.frame_1 = frame_1
            # Top Label
        TopLabel = customtkinter.CTkLabel(master=frame_1, text="Download Video From URL")
        TopLabel.pack(pady=0, padx=10, anchor="w")

        # Video URL Text Input
        self.urlEntry = customtkinter.CTkEntry(master=frame_1, placeholder_text="Video URL")
        self.urlEntry.pack(pady = (0, 0), padx = 10, ipadx = 1000, anchor = "w")

        # Top Button Section
        TopButtonFrame = customtkinter.CTkFrame(master=frame_1)
        TopButtonFrame.pack(fill="x", pady=(0,0))
        TopButtonFrame.grid_columnconfigure(0, weight=1)
            # Grab Video Button
        GrabVideo_Button = customtkinter.CTkButton(master = TopButtonFrame, command = self.GrabVideo_Callback, text = "Grab Video", width = 100)
        GrabVideo_Button.grid(row=1, column=4, sticky="e", pady=10)
            # Download Thumbnail Button
        DownloadThumbnail_Button = customtkinter.CTkButton(master = TopButtonFrame, command = self.DownloadThumbnail, text = "Download Thumbnail")
        DownloadThumbnail_Button.grid(row=1, column=2, sticky="e", pady=10, padx=10)

        # Video Title Label
        VideoTitle_Label = customtkinter.CTkLabel(master=frame_1, textvariable=self.handler.VideoTitle)
        VideoTitle_Label.pack(pady=0, padx=10, anchor="w")

        # Load default thumbnail
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./bin")
        self.Thumbnail = customtkinter.CTkImage(light_image=Image.open(os.path.join(self.image_path, f"DefaultImage.jpg")),size=(127*3,72*3))
        self.ThumbnailLabel = customtkinter.CTkLabel(master=self.frame_1, text="", image=self.Thumbnail)
        self.ThumbnailLabel.pack()

        # Start of Resolution/Quality Selection Section
        frame_2 = customtkinter.CTkFrame(master=frame_1)
        frame_2.pack(fill="x", pady=(0,0))
            # MP3/MP4 Selection Button
        self.segmented_button = customtkinter.CTkSegmentedButton(master=frame_2, values=["MP3", "MP4"], command=self.ModeSwap)
        self.segmented_button.grid(row=4, column=0, padx=10, pady=10)
        self.segmented_button.set("MP3")
            # Resolution Dropdown Menu
        resolution = custom_CTkComboBox(master=frame_2, values=["No Options Found"], button_color="#3B8ED0", state="readonly")
        resolution.grid(row=4, column=1, sticky="w", pady=10)
        resolution.set("Quality (Unset)")
        resolution._entry.configure(readonlybackground="#343638")
        self.resolution = resolution
            # Download Button
        button_1 = customtkinter.CTkButton(master = frame_2, text="Download", width=100, command=self.Download_Callback)
        button_1.grid(row=4, column=2, pady=10, padx=(20, 0), sticky="e")
        self.DownloadButton = button_1
        # End of Resolution/Quality Selection Section

        # Start of Bottom Status Section
            # Download Status Message
        statusLabel = customtkinter.CTkLabel(master = self, text="")
        statusLabel.pack(pady=0, padx=10, anchor="w")
        self.statusLabel = statusLabel
            # Download Progress Bar
        progressbar_1 = customtkinter.CTkProgressBar(master = self)
        progressbar_1.pack(pady = 0, padx = 10, fill="x")
        progressbar_1.set(0)
        progressbar_1.configure(mode="determinate")
        self.progressbar_1 = progressbar_1
        # End of Bottom Status Section

        self.previousDir = None



    def GrabVideo_Callback(self):
        self.handler.VideoURL.set(self.urlEntry.get())
        self.handler.GrabVideo()

        self.UpdateThumbnail()

        with open("./bin/videoData.json", "r") as videoDataFile:
            videoData = json.loads(videoDataFile.read())
        
        # This is a bit hacky, but its easier/more performant(?) than doing magic to make hashmaps work.
        self.VideoQualities = []
        self.AudioQualities = []
        # Iterate through resolutions
        # Replace any previously existing resolution with the same value

        for format in videoData.get("formats")[::-1]:
            format_res = format.get("resolution")
            if "audio only" in format_res:
                format_res += f" - {format.get('format_note')}"
                if format_res not in self.AudioQualities:
                    self.AudioQualities.append(format_res)
            else:
                if format_res not in self.VideoQualities:
                    self.VideoQualities.append(format_res)
        self.AudioQualities = self.AudioQualities[::-1]
        self.VideoQualities = self.VideoQualities[::-1]
        self.ModeSwap(self.segmented_button.get())
        self.UpdateThumbnail()

    def Download_Callback(self):
        self.handler.Progress = 0
        if self.handler.VideoURL.get() is None or self.handler.VideoURL.get() == "":
            return
        if self.resolution.get() == "Quality (Unset)" or self.resolution.get() == "No Options Found":
            return
        self.DownloadButton.configure(state="disabled")
        with open("./bin/videoData.json", "r") as videoDataFile:
            videoData = json.loads(videoDataFile.read())
        
        video_format = None

        selected_quality = self.resolution.get()

        for format in videoData.get("formats")[::-1]:
            if format.get("resolution") == selected_quality:
                video_format = format.get("format_id")
                break
            elif format.get("resolution") == "audio only" and selected_quality.split(" - ") == format.get('format_note'):
                video_format = format.get("format_id")
                break
                
        # self.handler.Download()
        file_type = self.segmented_button.get()
        self.filename = filedialog.asksaveasfilename(initialdir = "./" if self.previousDir is None else self.previousDir,
                        defaultextension = file_type.lower(), title = "Save File As...", filetypes = ((f"{file_type} Files", f"*.{file_type.lower()}"),("All files","*.*")))
        if self.filename is None or self.filename == "":
            self.DownloadButton.configure(state="normal")
            return
        self.previousDir = os.path.dirname(self.filename)


        self.downloadThread = Thread(target=self.handler.DownloadVideo, args=(video_format, self.filename))
        self.downloadThread.start()

        #self.handler.DownloadVideo(video_format, self.filename)

        pollerThread = Thread(target=self._pollProgress, args=())
        pollerThread.start()
        
    def DownloadThumbnail(self):
        thumbnailURL = self.handler.VideoThumbnailURL.get()
        image_ext = thumbnailURL.split(".")[-1]
        image_filename = filedialog.asksaveasfilename(initialdir = "./" if self.previousDir is None else self.previousDir, 
                                                    defaultextension = image_ext.lower(),
                                                    title = "Save File As...",
                                                    filetypes = ((f"{image_ext.upper()} Files", f"*.{image_ext.lower()}"),("All files","*.*")))
        if image_filename == "" or image_filename is None:
            return
        self.previousDir = os.path.dirname(image_filename)

        image_req = get(thumbnailURL)
        if image_req.status_code == 200:
            img = open(image_filename, "wb")
            img.write(image_req.content)
            img.close()
        os.startfile(os.path.dirname(image_filename))

    def ModeSwap(self, mode):
        if mode == "MP3":
            self.resolution.configure(values=self.AudioQualities)
        else:
            self.resolution.configure(values=self.VideoQualities)
        self.resolution.set("Quality (Unset)")

    def UpdateThumbnail(self):
        image_path = self.image_path
        image_url = self.handler.VideoThumbnailURL.get()
        image_ext = image_url.split(".")[-1]
        image_req = get(image_url)

        if image_req.status_code == 200:
            for bin_file in os.listdir(image_path):
                if "thumbnail_preview" in bin_file:
                    os.remove(os.path.join(image_path, bin_file))
            img = open(
                os.path.join(image_path, f"thumbnail_preview.{image_ext}"), "wb"
            )
            img.write(image_req.content)
            img.close()
        self.Thumbnail.configure(light_image=Image.open(os.path.join(image_path, f"thumbnail_preview.{image_ext}")))

    def _pollProgress(self): 
        progress = self.handler.Progress
        while progress != 1 and self.downloadThread.is_alive():
            time.sleep(0.1)
            updated_progress = self.handler.Progress
            if updated_progress != progress:
                self.progressbar_1.set(updated_progress)
                progress = updated_progress
            self.statusLabel.configure(text=self.handler.Status)

        self.statusLabel.configure(text="Download is Complete!")
        self.progressbar_1.set(1)
        self.GrabVideo_Callback()
        self.DownloadButton.configure(state="normal")

    def Boot(self):
        self.mainloop()
if __name__ == "__main__":  
    app = MainWindow("400x450", "TubeDownloader")
    app.Boot()