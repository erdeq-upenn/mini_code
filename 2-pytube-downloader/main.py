# !bin/sh
import numpy as py
import sys
import time
import os
from pytube import YouTube
import ffmpeg

def main(url):
    t0 = time.time()
    try:
        yt = YouTube(url)
        yt.streams.filter(only_audio=True,mime_type='audio/mp4').order_by('abr').desc().first().download()
    except:
        print('error')
    audio_title  = yt.title 
    audio_length = yt.length
    print("Audio length is : ",audio_length)
    print("Audio title  is : ",audio_title)

    stream = ffmpeg.input(audio_title+'.mp4')
    stream = ffmpeg.output(stream, audio_title+'_p.mp4')
    ffmpeg.run(stream)
    os.remove(audio_title+'.mp4')
    t1 = time.time()
    print('Done downloading %s in %.2f s'%(audio_title,t1-t0))

if __name__ == '__main__':
    LOG_DIR = '/log'
    url = sys.argv[1]
    main(url)
