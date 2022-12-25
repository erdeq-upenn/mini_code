import os
import sys
import logging as log

logger = log.getLogger(__name__)  # pylint: disable=invalid-name

def build(args):
    if args.cuda==0:
        log.info('Cuda version %s'%args.cuda)
    else:
        log.info('cuda other')
