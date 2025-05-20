from pytubefix import YouTube
from pytubefix.cli import on_progress


# # download video with highest resolution 
# url = "https://www.youtube.com/watch?v=ekr2nIex040"

# yt = YouTube(url, on_progress_callback=on_progress)
# print(yt.title)

# ys = yt.streams.get_highest_resolution()
# ys.download()


# download audio only 
from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "https://www.youtube.com/watch?v=ekr2nIex040"

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_audio_only()
ys.download(output_path="data/audio")