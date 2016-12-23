# -*- coding:utf-8 -*-

"""
@author:itgao
@file: mapper_gen.py
@time: 2016/12/6 21:03
根据 MAP 生成 Mapper配置文件
"""
from SQL import getTableInfo
import setting

header = '''<!DOCTYPE mapper
    PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="{0}.{1}">'''.format(setting.DAO_TARGET_PACKAGE,setting.ENTITY_NAME+'Dao')
result = '<result property="{0}" column="{1}" />\n'
result_header_start = '\t<resultMap type="{0}.{1}" id="BaseResultMap">'\
    .format(setting.ENTITY_TARGET_PACKAGE,setting.ENTITY_NAME)
result_header_end = '\t</resultMap>'
insert_start = '\n\t<insert id="save" parameterType="{0}.{1}">'.format(setting.ENTITY_TARGET_PACKAGE,setting.ENTITY_NAME)
insert_end = '\n\t</insert>'
update_start = '\n\t<update id="update" parameterType="{0}.{1}">'.format(setting.ENTITY_TARGET_PACKAGE,setting.ENTITY_NAME)
update_end = '\n\t</update>'
delete_start = '\n\t<delete id="delete" parameterType="int">'
delete_end = '\n\t</delete>'
select_start = '\n\t<select id="select" parameterType="int" resultType="{0}.{1}">'.format(setting.ENTITY_TARGET_PACKAGE,setting.ENTITY_NAME)
select_end = '\n\t</select>'


def generate():
    maps = getTableInfo()
    resultMap = result_header_start+"\n"
    insert = insert_start+'\n\t\tinsert to '+setting.TABLE_NAME+' VALUES('
    id = maps.values()[0].keys()[0]
    delete = delete_start+'\n\t\tdelete from '+setting.TABLE_NAME+' where '+id+' = #{'+id+'}'+delete_end
    select = select_start+'\n\t\tselect * from '+setting.TABLE_NAME+' where' +id+' = #{'+id+'}'+select_end
    update = update_start+'\n\t\tupdate table '+setting.TABLE_NAME+' set '
    index = 0
    resultMap += '\t\t<id property="'+id+'" column="'+id+'" />\n'
    for map in maps.values():
        key = map.keys()[0]
        if index != 0:
            resultMap += '\t\t'+result.format(key,key)+"\n"
        insert += '#{'+key+'},'
        if index != 0:
            update += key+' = #{'+key+'},'
        index += 1
    resultMap += result_header_end
    insert = insert[:-1]+insert_end
    update = update[:-1]+'where '+id+' = #{'+id+'}'+update_end
    content = header+'\n'+resultMap+insert+update+select+delete+'\n</mapper>'
    return content
if __name__ == '__main__':
    generate()