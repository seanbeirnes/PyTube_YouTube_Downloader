#Import modules
import sys
import os
import re
from pathlib import Path
from pytube import YouTube
import ffmpeg

####################################################################################################
##### GENERAL FUNCTIONS
####################################################################################################

# Validates if a url follows a valid YouTube video URL syntax
def isValidYouTubeUrl(url):
    URL_PATTERN = r"^(?:https?:\/\/)(?:.+oembed.+)?(?:m\.|www\.)?(?:(?:youtube(?:\-nocookie)?\.com)|(?:youtu\.be))\/(?:(?:.*watch%3Fv%3D)|(?:(?:(?:watch\?(?:[a-z]+=[a-z_&]+)?v(?:=|%3D))|(?:(?:e\/)|(?:v\/)))?|(?:embed\/)))([a-zA-Z0-9_\-]{11})(?!.*http|[\.a-zA-Z]{3})"
    return re.match(URL_PATTERN, url)


####################################################################################################
##### USER INPUT FUNCTIONS
####################################################################################################

# Shows user a message and asks for confirmation. Return boolean value.
def getUserConfirmation(message):

    while True:
        print(message + " (y/N)")
        userInput = input()

        if userInput.strip().lower() == "n":
            return False
        if userInput.strip().lower() == "y":
            return True
        else:
            print("Error: incorrect input value. Please enter y/N")


# Sets the default save path in the user's Downloads folder or lets user input a different path and validates it
def getSavePath():
    save_path = str(Path.home() / "Downloads")

    useDifferentPath = getUserConfirmation(f"The deafult save path is {save_path}\nWould you like to define a different path?")

    if useDifferentPath == False:
        return save_path
    
    while True:
        print("Please enter a new directory path:")
        userInput = input()

        if os.path.isdir(userInput):
            if getUserConfirmation(f"Would you like to set the new path as {userInput} ?"):
                save_path = userInput
                return save_path
        else:
            print("Error: Directory does not exist.")
            if not getUserConfirmation(f"Would you like to try again?"):
                return save_path


# Retrieves and validates a YouTube url from a user
def getUrl():
    while True:
        print("Please enter the full YouTube video url or N to exit:")

        url = input()

        if isValidYouTubeUrl(url):
            return url
        if url.strip().lower() == "n":
            sys.exit()
        else:
            print("Error: URL entered is invalid. Please try again...")


####################################################################################################
##### DOWNLOAD FUNCTIONS
####################################################################################################

# Checks if the YouTube video has a resolution higher than 720p
def isResHigherThan720(yt: YouTube):
    resolutions = ["2160p", "1080p"]

    for resolution in resolutions:
        result = yt.streams.filter( res=resolution )
        if result:
            return True
    
    return False


# Downloads the highest resolution available
def downloadHighRes(url, save_path, yt: YouTube):
    print(f"### Found High Resolution Video ###")

    print(f"Downloading high resolution video only file from '{url}'")
    vidStream = yt.streams.filter(only_video=True).order_by("resolution").last()
    videoFileName = "video_" + vidStream.default_filename
    vidStream.download( output_path=save_path, filename=videoFileName )

    print(f"Downloading high resolution audio only file from '{url}'")
    audioStream = yt.streams.filter(only_audio=True).order_by("abr").last()
    audioFileName = "audio_" + audioStream.default_filename
    audioStream.download( output_path=save_path, filename=audioFileName )

    print("Download complete!")

    return( {"defaultFileName": vidStream.default_filename.rsplit(".", 1)[0] + ".mp4", "videoFileName": videoFileName, "audioFileName": audioFileName} )


# Combines a video-only and audio-only file into a new file, then deletes old files.
def processDownload(newFilePath, videoFilePath, audioFilePath):
    print(f"Combining video and audio files into: {newFilePath}\nThe old files will be removed when finished.")

    video = ffmpeg.input(videoFilePath)
    audio = ffmpeg.input(audioFilePath)

    ffmpeg.concat(video, audio, v=1, a=1).output(newFilePath).run()

    os.remove(videoFilePath)
    os.remove(audioFilePath)

# Downloads the highest resolution availble under 720p
def downlaodStandardRes(url, save_path, yt: YouTube):
    print(f"Downloading standard resolution video from '{url}'")
    yt.streams.filter( file_extension="mp4" ).get_highest_resolution().download( output_path=save_path )

    print("Download complete!")


# Makes a download progress bar when bound to the PyTube downloader
def progress_function(stream, chunk, bytes_remaining):
    current = ((stream.filesize - bytes_remaining)/stream.filesize)
    percent = ('{0:.1f}').format(current*100)
    progress = int(50*current)
    status = '█' * progress + '-' * (50 - progress)
    sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
    sys.stdout.flush()


# Main download function. Used to switch between standard and high res downloads
def download(url, save_path):
    yt = YouTube(url)
    yt.register_on_progress_callback(progress_function)

    if isResHigherThan720(yt):
        fileNames = downloadHighRes(url, save_path, yt)
        processDownload( 
                        newFilePath = os.path.join( save_path, fileNames["defaultFileName"] ),
                        videoFilePath = os.path.join( save_path, fileNames["videoFileName"] ), 
                        audioFilePath = os.path.join( save_path, fileNames["audioFileName"] ) 
                        )

    else:
        downlaodStandardRes(url, save_path, yt)


####################################################################################################
##### MAIN
####################################################################################################

# Main function
def main():
    print("Welcome to the YouTube Downloader.")

    # Get save path and video URL
    save_path = getSavePath()

    while True:
        url = getUrl()  

        # Download the video
        download(url, save_path)

        if getUserConfirmation("Would you like to download another video?") == False:
            print("Goodbye")
            sys.exit()


# Run
main()
