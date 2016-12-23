# -*- coding:utf-8 -*-

"""
@author:itgao
@file: SQL.py
@time: 2016/12/6 19:51
将对应表中的字段和属性全部取出，按顺序形成MAP
"""
import MySQLdb
import re
import setting


def connectSQL():
    db = MySQLdb.connect('localhost','root','root',setting.DATA_BASE,charset='utf8')
    cursor = db.cursor()

    return db,cursor


def getTableInfo():
    db,cursor = connectSQL()
    sql = "desc "+setting.TABLE_NAME #将表中所有属性和类型列出来
    cursor.execute(sql)
    maps = {}

    mat = '(.*?)('

    data = cursor.fetchall()
    i = 0
    for da in data:
    #    print da
        da = list(da)
        index = da[1].find('(')
        if index >= 0:
            da[1] = da[1][:index]
        maps[i] = {da[0]:setting.TRANS[da[1]]}
        i += 1

    db.close()
    return maps




if __name__ == '__main__':
    getTableInfo()