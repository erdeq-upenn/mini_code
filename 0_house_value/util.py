# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 15:50:21 2022

@author: dequan

import functions
"""
import numpy as np
import numpy_financial as npf
import sys
import time
import os
import matplotlib.pyplot as plt

def npv(cf,r) -> float:
    # corporate finance npv function
    n = len(cf)
    res = 0
    for i,v in enumerate(cf):
        res += v*(1+r)**(-i)
    return res

def irr(cf):
    return npf.irr(cf)


def main():
    print('import functions')
    
if __name__ == '__main__':
    LOG_DIR = '../log'
    main()