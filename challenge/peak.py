# -*- coding:utf-8 -*-

"""
@author:itgao
@file: peak.py
@time: 2016/12/20 15:13
"""

# data banner.p

import pickle

banner = pickle.load(open('data/banner.p','r'))
for line in banner:
    print ''.join(ch * count for ch ,count in line)