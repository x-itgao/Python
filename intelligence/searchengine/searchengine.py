# -*- coding:utf-8 -*-

"""
@author:itgao
@file: searchengine.py
@time: 2016/12/25 23:15
"""
import urllib2
import re
from bs4 import *
from urlparse import urljoin
import MySQLdb

ignore_words = set(['the','of','to','and','a','in','is','it'])

class crawler:

    # 传入数据库名字
    def __init__(self):
        self.conn = MySQLdb.connect("localhost","root","root","intelligence",charset="utf8")
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def db_commit(self):
        self.conn.commit()

    # 用于获取条目的ID，如果不存在，就将其加入到数据库中
    def get_entry_id(self,table,field,value,create_new=True):
        self.cursor.execute("select id from %s where %s='%s'"%(table,field,value))
        res = self.cursor.fetchone()
        print 'entry_id',res
        if res is None:
            cur = self.cursor.execute("insert into %s (%s) values ('%s')"%(table,field,value))
            self.db_commit()
            print 'insert',value
            self.cursor.execute("select last_insert_id() from %s"%table)
            lastid = self.cursor.fetchone()
            if type(lastid) is tuple:
                return lastid[0]
            else:
                return lastid
        else:
            print 'res[0]',res[0]
            return res[0]

    def add_to_index(self,url,soup):
        if self.is_indexed(url):
            return
        text = self.get_text_only(soup)
        words = self.separate_words(text)
        url_id = self.get_entry_id('urllist','url',url)
        for i in range(len(words)):
            word = words[i]
            if word in ignore_words:
                continue
            word_id = self.get_entry_id('wordlist','word',word)
            sql = "insert into wordlocation(urlid,wordid,location)VALUES (%d,%d,%d)"%(url_id,word_id,i)
            self.cursor.execute(sql)
            self.db_commit()

    # 获取纯文本
    def get_text_only(self,soup):
        v = soup.string
        if v is None:
            c = soup.contents
            result_text = ''
            for t in c:
                sub_text = self.get_text_only(t)
                result_text+=sub_text+'\n'
            return result_text
        else:
            return v.strip()

    # 根据任何非空白字符进行分词处理
    def separate_words(self,text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']

    # 如果已经建立过索引，就返回True
    def is_indexed(self,url):
        self.cursor.execute("select id from urllist where url='%s'"%url)
        u = self.cursor.fetchone()
        if u is not None:
            self.cursor.execute("select * from wordlocation where urlid='%d'"%u[0])
            v = self.cursor.fetchone()
            if v is not None:
                return True
        return False

    # 添加一个关联两个网页的链接
    def add_link_ref(self,url_from,url_to,link_text):
        words = self.separate_words(link_text)
        from_id = self.get_entry_id('urllist','url',url_from)
        to_id = self.get_entry_id('urllist','url',url_to)
        if from_id == to_id:
            return
        print from_id,to_id
        sql = "insert into link(fromid,toid)VALUES (%d,%d)"%(from_id,to_id)
        self.cursor.execute(sql)
        self.db_commit()
        self.cursor.execute("select last_insert_id() from link")
        link_id = self.cursor.fetchone()
        if type(link_id) is tuple:
            link_id = link_id[0]
        for word in words:
            if word in ignore_words:
                continue
            word_id = self.get_entry_id('wordlist','word',word)
            sql = "insert into linkwords(linkid,wordid)VALUES (%d,%d)" %(link_id,word_id)
            self.cursor.execute(sql)
            self.db_commit()
    # 广度优先搜索直至到达某一深度
    def crawl(self,pages,depth = 2):
        for i in range(depth):
            new_pages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print "Could not open %s" %page
                    continue
                soup = BeautifulSoup(c.read(),"lxml")
                print 'add_to_index starting......'
                self.add_to_index(page,soup)

                links = soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page,link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        if url[0:4] == 'http' and not self.is_indexed(url):
                            new_pages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page,url,link_text)
                self.db_commit()
            pages = new_pages

    def create_index_tables(self):
        self.cursor.execute('create table urllist(id int primary key auto_increment,url VARCHAR(100) )')
        self.cursor.execute('create table wordlist(id int PRIMARY KEY auto_increment,word VARCHAR (20))')
        self.cursor.execute('create table wordlocation(id int PRIMARY KEY auto_increment,urlid int,wordid int,location VARCHAR(50) )')
        self.cursor.execute('create table link(id int PRIMARY KEY auto_increment,fromid INTEGER ,toid INTEGER)')
        self.cursor.execute('create table linkwords(id int PRIMARY KEY auto_increment,wordid VARCHAR(20),linkid INT )')
        self.cursor.execute('create index wordidx on wordlist(word)')
        self.cursor.execute('create index urlidx on urllist(url)')
        self.cursor.execute('create index wordurlidx on wordlocation(wordid)')
        self.cursor.execute('create index urltoindex on link(toid)')
        self.cursor.execute('create index urlfromidx on link(fromid)')
        self.db_commit()


class Searcher:

    def __init__(self):
        self.conn = MySQLdb.connect("localhost","root","root","intelligence",charset="utf8")
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def get_match_rows(self,q):
        # 构造查询的字符串
        field_list = 'w0.urlid'
        table_list = ''
        clause_list = ''
        word_ids =  []

        # 根据空格拆分单词
        words = q.split(' ')
        table_number = 0
        print words
        for word in words:
            self.cursor.execute("select id from wordlist where word='%s'"%word)
            word_row = self.cursor.fetchone() # 从wordlist中查找到id
            if word_row is not None:
                word_id = word_row[0]
                word_ids.append(word_id)
                if table_number > 0:
                    table_list += ','
                    clause_list += ' and '
                    clause_list += 'w%d.urlid=w%d.urlid and '%(table_number-1,table_number)
                field_list += ',w%d.location' % table_number
                table_list += 'wordlocation w%d' % table_number
                clause_list += 'w%d.wordid=%d' %(table_number,word_id)
                table_number += 1
        # 根据各个分组 建立查询
        full_query = 'select %s from %s where %s'%(field_list,table_list,clause_list)
        print full_query
        self.cursor.execute(full_query)

        rows = [row for row in self.cursor.fetchall()]
        return rows,word_ids

    def get_scored_list(self,rows,wordids):
        total_scores = dict([(row[0],0) for row in rows])
        # 评价函数
        weights = [(1.0,self.frequency_score(rows))]
        for (weight,scores) in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]
        return total_scores

    def get_url_name(self,id):
        self.cursor.execute("select url from urllist where id=%d" % id)
        return self.cursor.fetchone()[0]

    def query(self,q):
        rows,word_ids = self.get_match_rows(q) # 网页index 位置
        scores = self.get_scored_list(rows,word_ids)
        ranked_cores = sorted([(score,url) for (url,score) in scores.items()],reverse=1)
        for (score,url_id) in ranked_cores[0:10]:
            print '%f\t%s' % (score,self.get_url_name(url_id))

    # 归一化函数 使数据具有相同的值域及变化方向，根据每个评价值与最佳结果的接近程度
    def normalize_scores(self,scores,small_is_better=0):
        v_small = 0.00001
        if small_is_better:
            min_score = min(scores.values())
            return dict([(u,float(min_score)/max(v_small,l)) for (u,l) in scores.items()])
        else:
            max_score = max(scores.values())
            if max_score == 0:
                max_score = v_small
            return dict([(u,float(c) / max_score) for (u,c) in scores.items()])

    # 单词频度
    def frequency_score(self,rows):
        counts = dict((row[0],0) for row in rows)
        for row in rows:
            counts[row[0]] += 1
        return self.normalize_scores(counts)

if __name__ == '__main__':

    page_list = ['http://en.people.cn/']
    craw = crawler()
    # craw.create_index_tables()
    craw.crawl(page_list)
    #test = "insert into ss(id,ukr)VALUES (%d,%d)"%(1,2)
    #print test
    #l = [row for row in craw.cursor.execute('select * from wordlocation').fetchall()]
    #print l
    # searcher = Searcher()
    # print searcher.get_match_rows("test new party")
    # searcher.query("new test")



