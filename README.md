# TubeDownloader
A YT_DLP desktop interface.

![image](https://user-images.githubusercontent.com/117033048/207522911-4ec91866-d0d8-44a5-bf35-3c5f348e947c.png)


## Requirements
- Requires [ffmpeg.exe](https://ffmpeg.org/download.html) in `/TubeDownloader/bin`
- Building the Installer requires InstallForge

## Installation
1. Run the installer .exe from the [releases](https://github.com/pelpadesa/TubeDownloader/releases) page
2. Then, you can find a TubeDownloader Start menu shortcut which will open the application.

Or download the .zip, extract the files, then run TubeDownloader.exe

## Compiling the Source
You can compile the project using pyinstaller, I recommend the arguments:
```
--noconfirm --onedir --windowed --name "TubeDownloader"
--add-data "/TubeDownloader/__init__.py;."
--add-data "/TubeDownloader/bin;bin/"
--add-data ".../Python310/Lib/site-packages/customtkinter;customtkinter/" [Adjust to your python path]
--hidden-import "yt_dlp"
"/TubeDownloader/Main.pyw"
```
(You can find customtkinter's location using `pip show customtkinter`)

The output project should work as intended, but if you want you can build the .ifp Installer project using InstallForge & adjust the filepaths as needed.
