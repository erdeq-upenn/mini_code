'''This is a test of std parser'''
import os
import sys
import time
import copy
import random
import argparse
import logging as log
import _pickle as pkl


def main(arguments):
    ''' Train or load a model. Evaluate on some tasks. '''
    parser = argparse.ArgumentParser(description='')

    # Logistics
    parser.add_argument('--cuda', help='-1 if no CUDA, else gpu id', type=int, default=0)

    # path and logging
    parser.add_argument('--log_file', help='file to log to', type=str, default='log.log')
    parser.add_argument('--exp_dir', help='directory containing shared preprocessing', type=str)
    parser.add_argument('--run_dir', help='directory for saving results, models, etc.', type=str)

    args = parser.parse_args(arguments)
    log.basicConfig(format='%(asctime)s: %(message)s', level=log.INFO, datefmt='%m/%d %I:%M:%S %p')
    log_file = os.path.join(args.run_dir, args.log_file)
    file_handler = log.FileHandler(log_file)
    log.getLogger().addHandler(file_handler)
    log.info(args)

    log.info("Loading tasks...")
    print(args)
    print('Done---')

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
