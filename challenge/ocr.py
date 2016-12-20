# -*- coding:utf-8 -*-

"""
@author:itgao
@file: ocr.py
@time: 2016/12/20 10:43
"""

# ocr.data里面是challenge给出的数据

with open('ocr.data','r') as file:
    page_data = file.read()
file.close()
data_map = {}
# 获取出现的key及次数
for chr in page_data:
    data_map.setdefault(chr,0)
    if chr in data_map.keys():
        data_map[chr] += 1

# 获取最小次数
min_value = min(data_map.values())

# 获取最小次数对应单词
min_data = [(key,value) for key,value in data_map.items() if value==min_value]

# 按照出现次序排列
sorted_list = ''.join([chr[0] for chr in sorted(min_data,key=lambda x:page_data.find(x[0]))])
print sorted_list

