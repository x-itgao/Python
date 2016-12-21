# -*- coding:utf-8 -*-

"""
@author:itgao
@file: deliciousrec.py
@time: 2016/12/20 21:21
pydelicious 访问del.icio.us网站获取数据的Api
"""
import time
from pydelicious import get_popular,get_userposts,get_urlposts


def init_userdict(tag,count=5):
    user_dict = {}
    # 获取前count个最受欢迎的链接张贴记录
    for p1 in get_popular(tag=tag)[0:count]:
        if p1['url'] != '':
            for p2 in get_urlposts(p1['url']):
                user = p2['user']
                user_dict[user] = {}
    return user_dict


def fill_items(user_dict):
    all_items = {}
    # 所有用户都提交过的链接
    for user in user_dict:
        for i in range(3):
            try:
                posts = get_userposts(user)
                break
            except:
                print "Falied user "+user+", retrying"
                time.sleep(4)
        for post in posts:
            url = post['href']
            user_dict[user][url] = 1.0
            all_items[url] = 1
        # 用0填充缺失的项
        for ratings in user_dict.values():
            for item in all_items:
                if item not in ratings:
                    ratings[item] = 0.0


if __name__ == '__main__':
    delusers = init_userdict('programming')
    print delusers
    delusers['tsegaran'] = {}
    fill_items(delusers)
    print delusers

















































































