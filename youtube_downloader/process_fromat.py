# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:50:41 2022
update on 12/28
@author: dequan er
"""
import os,shutil,glob
import sys
import time
import copy
import random
import argparse
import logging as log
import _pickle as pkl
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter,Formatter
from pytube import YouTube
import argparse
import re
import ffmpeg

def process_audio(audio_title):
    print("Audio title  is : ",audio_title)
    try:
        stream = ffmpeg.input(audio_title + '.mp4')
        stream = ffmpeg.output(stream, audio_title + '_p' + '.mp4')
        ffmpeg.run(stream)
        os.remove(audio_title+'.mp4')
        shutil.move(audio_title+'_p.mp4',os.path.join('data',audio_title+'_p.mp4'))    
    except:
        print('ffmpeg naming error, exiting...')
        sys.exit(1)

audio_list = glob.glob('*.mp4')
for ii in audio_list:
    print(ii[:-4]) 
    process_audio(ii[:-4])
