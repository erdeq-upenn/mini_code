# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:50:41 2022

@author: dequan er
"""

import os
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

def download_script(args):
    formatter = Formatter()
    video_id = args.id
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_manually_created_transcript(['zh-Hans'])
    ts = transcript.fetch()
    ts_txt = ','.join([i['text'] for i in ts])

    url = 'https://youtu.be/' + video_id
    title = YouTube(url).title
    try:
        title = title.split('|')[1]
        title = ''.join(re.findall(r'[\u4e00-\u9fa5]',title))
    except:
        print('Title not splitable...')
        pass

    with open('%s/%s.txt'%(args.data_dir,title),'w',encoding='utf-8') as f:
        f.write(ts_txt)
    f.close()

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
    # start donwload task
    download_script(args)
    log.info('\tFinished loading tasks in %.3fs', time.time() - start_time)

    print('Done---')

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
