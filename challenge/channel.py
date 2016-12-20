# -*- coding:utf-8 -*-

"""
@author:itgao
@file: channel.py
@time: 2016/12/20 15:35
"""
import re,zipfile
# data dir channel

num = '94191'
comments = []
f = zipfile.ZipFile('data/channel.zip','r')
while True:
    fname = '{}.txt'.format(num)
    comments.append(f.getinfo(fname).comment)
    data = f.read(fname)
    res = re.findall(r'\d+$',data)
    if res:
        num = res[0]
    else:
        break
print ''.join(comments)
