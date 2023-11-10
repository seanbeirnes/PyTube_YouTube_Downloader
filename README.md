# PyTube_YouTube_Downloader
Python script for downloading personal YouTube videos at their original resolution if the original files were lost.

## Dependencies
```
import sys
import os
import re
from pathlib import Path
from pytube import YouTube
import ffmpeg
```

## Important Notice
This code is intended for the purpose of downloading one's own videos from YouTube if the original source files were lost. It is not intended for other uses, espeiclaly those of which may break YouTube's Terms of Service. 

## Use Case
YouTube by default will only let you download your videos up to 720p resolution from the web GUI. If you uploaded your video at a higher resolution, you will need an alternative method to download it at it's original resolution. This script will find the highest resolution of your video available and download it. Videos at 720p resolution and under are downloaded as a single .mp4 file. Videos with a resolution higher than 720p are stored in YouTube with the audio and video files separated. This script will download the separate video and audio files, and then it will use ffmpeg to combine them. The source audio and video files will be deleted so you are left with just a single .mp4 video file.

## Create Excutable
You can use PyInstaller to compile the code into a single console application so you can use the script without a code editor.
```
pyinstaller -F -c main.py
```
