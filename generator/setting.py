# -*- coding:utf-8 -*-

"""
@author:itgao
@file: setting.py
@time: 2016/12/6 19:35
保存了配置信息，包括文件名，放置位置，对应转化
"""

# mysql数据库、用户名、密码
DATA_BASE = 'highschoolcheck'
USER_NAME = 'root'
PASS_WORD = 'root'

# 生成模型的包名和位置
ENTITY_TARGET_PACKAGE = 'com.halfmoon.cloudmanager.model'
ENTITY_TARGET_PROJECT = 'src'

# 生成映射文件的包名和位置
MAPPER_TARGET_PACKAGE = 'com.halfmoon.cloudmanager.mapper'
MAPPER_TARGET_PROJECT = 'src'

# 生成DAO文件的包名和位置
DAO_TARGET_PACKAGE = 'com.halfmoon.cloudmanager.dao'
DAO_TARGET_PROJECT = 'src'

# 要生成的表名，模型名字
TABLE_NAME = 'single_sign_check'
ENTITY_NAME = 'Single_Sign_Check'

# MYSQL和Java中类型对应
TRANS = {
    'varchar':'String',
    'char':'String',
    'datetime':'Date',
    'date':'Date',
    'text':'String',
    'int':'int',
    'json':'Object',
	'decimal':'double'
}

