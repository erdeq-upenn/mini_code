import numpy as py
import sys
import time
import os

def main():
    t0 = time.time()
    p0 = int(sys.argv[2])
    year = 2022- int(sys.argv[1])
    p1 = 1.03**year*p0
    p2 = 1.05**year*p0
    print("True value of House in 2022 is\nbetween %.2f and %.2f"%(p1,p2))
    t1 = time.time()
    print('time used %.3f ms'%((t1-t0)*1000))

if __name__ == '__main__':
    LOG_DIR = '/log'
    main()
