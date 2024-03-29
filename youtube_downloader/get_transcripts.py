# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:50:41 2022
update on 12/28
@author: dequan er
"""
import os,shutil
import sys
import time
import copy
import random
import argparse
import logging as log
import _pickle as pkl
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter,Formatter
from pytube.cli import on_progress
from pytube import YouTube
import argparse
import re
import ffmpeg
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime


def now_str():
    """
    return current date-time as a string like: 2020-01-01 18:20:30
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def download_script(args):
    formatter = Formatter()
    video_id = args.id
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_manually_created_transcript(['zh-Hans'])
    ts = transcript.fetch()
    ts_txt = ','.join([i['text'] for i in ts])

    url = 'https://youtu.be/' + video_id
    title = YouTube(url).streams[0].title
    print(title)
    try:
        title = title.split('|')[1]
        title = ''.join(re.findall(r'[\u4e00-\u9fa5]',title))
    except:
        print('Title not splitable...')
        pass

    with open('%s/%s.txt'%(args.data_dir,title),'w',encoding='utf-8') as f:
        f.write(ts_txt)
    f.close()

def download_script_srt(args):
    # This will download in srt format and convert to txt 
    # if there is a pause, automatic generate paragraphs
    # Current only work on zh CN 

    formatter = Formatter()
    video_id = args.id

    url = 'https://youtu.be/' + video_id
    yt = YouTube(url)
    yt.streams

    title = YouTube(url).streams[0].title
    try:
        title = title.split('|')[1]
        title = ''.join(re.findall(r'[\u4e00-\u9fa5]',title))
    except:
        print('Title not splitable...')
        pass

    # fetch srt and convert to txt based on time 
    caption = yt.captions.get_by_language_code('zh-Hans')
    cpation_srt = caption.generate_srt_captions()
    ss = cpation_srt.split('\n\n')
    colname = ['index','start','mark','end','description']
    res = []
    for s in ss:
        record = dict(zip(colname,s.split()))
        res.append(record)

    df = pd.DataFrame(res)
    df.start = pd.to_datetime(df.start)
    df.end = pd.to_datetime(df.end)
    df['new_line'] = np.where((df.start-df.end.shift(1)) > pd.Timedelta('00:00:00.2'), True, False)
    output = []

    def func(x,output):
        output.append(x['description'])
        output.append('。 ')

        if x['new_line']:
            output.append('\n\n')
    df.apply(lambda x: func(x,output),axis=1);
    ts_txt = ''.join(output)
         
    with open('%s/%s.md'%(args.data_dir,title),'w',encoding='utf-8') as f:
        f.write(ts_txt)
    f.close()

def download_audio(args):
    t0 = time.time()
    url = baseurl + args.id
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
    try:
       ffmpeg.run(stream)
       os.remove(audio_title+'.mp4')
       t1 = time.time()
       shutil.move(audio_title+'_p.mp4',os.path.join(args.data_dir,audio_title+'_p.mp4'))
    except:
       print('change name and retry...')
#     try:
#         process_audio(audio_title)
#         os.remove(audio_title+'.mp4')
#         shutil.move(audio_title+'_p.mp4',os.path.join(args.data_dir,audio_title+'_p.mp4'))
#     except:
#         audio_title_s = yt.title.split()[0]
#         shutil.move(audio_title,audio_title_s)
#         process_audio(audio_title_s)
#
#         os.remove(audio_title_s+'.mp4')
#         shutil.move(audio_title_s+'_p.mp4',os.path.join(args.data_dir,audio_title_s+'_p.mp4'))
#
# def process_audio(title):
#     print("Audio title  is : ",title)
#     try:
#         stream = ffmpeg.input(audio_title+'.mp4')
#         stream = ffmpeg.output(stream, audio_title+'_p.mp4')
#         ffmpeg.run(stream)
#     except:
#         print('ffmpeg naming error, exiting...')
#         sys.exit(1)
def download_video(args):
    t0 = time.time()
    url = baseurl + args.id
    print('Downloading URL: ',url)
    try:
        yt = YouTube(url,on_progress_callback=on_progress)
        yt.streams.filter(only_audio=False,mime_type='video/mp4').order_by('abr').desc().first().download()
        #yt.streams.get_highest_resolution().download()
    except:
        print('error')
    audio_title  = yt.title
    audio_length = yt.length
    print("Video length is : ",audio_length)
    print("Video title  is : ",audio_title)
    stream = ffmpeg.input(audio_title+'.mp4')
    stream = ffmpeg.output(stream, audio_title+'_p.mp4')
    try:
       ffmpeg.run(stream)
       os.remove(audio_title+'.mp4')
       t1 = time.time()
       shutil.move(audio_title+'_p.mp4',os.path.join(args.data_dir,audio_title+'_p.mp4'))
    except:
       print('change name and retry...')
def main(arguments):
    ''' Train or load a model. Evaluate on some tasks. '''
    parser = argparse.ArgumentParser(description='')

    # Logistics
    parser.add_argument('--id', help='youtube ID, not the url', type=str, default='')

    # download mode
    parser.add_argument('--mode', help='mode of download. "s" script,"a" audio, "v" video', choices=['s', 'a', 'v'],default='s')

    # path and logging
    parser.add_argument('--log_file', help='file to log to', type=str, default='log.log')
    parser.add_argument('--data_dir', help='directory containing shared preprocessing', type=str,default='data')
    parser.add_argument('--log_dir', help='directory for saving results, models, etc.', type=str,default='log')

    args = parser.parse_args(arguments)

    # logistics
    log.basicConfig(format='%(asctime)s: %(message)s', level=log.INFO, datefmt='%y-%m-%d %I:%M:%S %p')
    log_file = os.path.join(args.log_dir, args.log_file)
    file_handler = log.FileHandler(log_file)
    log.getLogger().addHandler(file_handler)
    log.info(args)

    log.info("Loading tasks...")
    start_time = time.time()
    # start donwload task of transcript
    if args.mode == 's':
        #download_script(args)
        print('Start Downloading script at $s...'%now_str())
        download_script_srt(args)
        log.info('\tFinished download script tasks in %.3fs', time.time() - start_time)
    if args.mode == 'a':
        download_audio(args)
        log.info('\tFinished download audio  tasks in %.3fs', time.time() - start_time)
    if args.mode == 'v':
        download_video(args)
        log.info('\tFinished download video  tasks in %.3fs', time.time() - start_time)
    print('Done---')

if __name__ == '__main__':
    baseurl = 'https://www.youtube.com/watch?v='
    sys.exit(main(sys.argv[1:]))
