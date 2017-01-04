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


    def calculate_page_rank(self,iterations=20):
        self.cursor.execute("drop table if EXISTS pagerank")
        self.db_commit()
        self.cursor.execute("create table pagerank(urlid INT PRIMARY KEY ,score FLOAT) ")
        self.db_commit()
        # 初始化每一个url，令PageRank值为1
        self.cursor.execute("insert into pagerank SELECT id,1.0 from urllist")
        self.db_commit()

        for i in range(iterations):
            print "Iteration %d" % i
            for (url_id,) in (self.cursor.execute("select id from urllist"),self.cursor.fetchall())[1]:
                pr = 0.15
                # 循环遍历指向当前网页的所有其他网页
                for (linker,) in (self.cursor.execute("select distinct(fromid) from link where toid=%d"%url_id),
                                                      self.cursor.fetchall())[1]:
                    # 得到链接源对应网页的PageRank值
                    linking_pr = (self.cursor.execute("select score from pagerank where urlid=%d"%linker),
                                  self.cursor.fetchone()[0])[1]
                    # 根据链接源，求得总的连接数
                    linking_count = (self.cursor.execute("select count(*) from link where fromid=%d"%linker),
                                                         self.cursor.fetchone()[0])[1]

                    pr += 0.85 * (linking_pr / linking_count)
                self.cursor.execute("update pagerank set score=%f where urlid=%d" % (pr,url_id))
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
        total_scores = dict([(row[0],0) for row in rows]) # [(index,0)]
        # 评价函数
        weights = [(1.0,self.location_score(rows)),(0.5,self.frequency_score(rows)),
                   (1.5,self.inbound_link_score(rows))]
        print "weights:",weights
        for (weight,scores) in weights:
            for url in total_scores:
                # print "url:",url
                #print "scores[url]:",scores[url]
                total_scores[url] += weight * scores[url]# 每一个网页都有了基本的数据 现在再乘以出现的次数
                print "total_scores:",total_scores[url]
        # 实际上scores和total_scores 没有变化
        return total_scores

    def get_url_name(self,id):
        self.cursor.execute("select url from urllist where id=%d" % id)
        return self.cursor.fetchone()[0]

    def query(self,q):
        rows,word_ids = self.get_match_rows(q) # rows:[urlid,word0.location,word1.location...] word_ids: wordlist.id
        scores = self.get_scored_list(rows,word_ids)
        print "scores:",scores
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
        counts = dict((row[0],0) for row in rows) # [(urlid,0)]
        for row in rows:
            counts[row[0]] += 1 # 网页出现的次数
        return self.normalize_scores(counts)

    # 根据单词出现的位置 越靠前相关度越高
    def location_score(self,rows):
        rows = map(lambda x : map(lambda y:int(y),x),list(rows))
        locations = dict([(row[0],1000000) for row in rows]) # [{index,1000000)]
        for row in rows:
            print row[1:]
            loc = sum(row[1:]) # row[1:] 后面是各个单词出现的位置index
            if loc < locations[row[0]]:
                locations[row[0]] = loc # 顺便还能找到同一个页面中最前面的数据
        return self.normalize_scores(locations,small_is_better=1)

    # 各个单词出现的距离，而且正确的顺序出现
    def distance_score(self,rows):

        rows = map(lambda x : map(lambda y:int(y),x),list(rows))
        if len(rows[0]) <= 2: # 如果只有一个单词 则无意义
            return dict([(row[0],1.0) for row in rows])

        min_distance = dict([(row[0],1000000) for row in rows])

        for row in rows:
            dist = sum([abs(row[i]-row[i-1]) for i in range(2,len(row))])# 2-len(row)-1 相互之间的距离之和
            if dist<min_distance[row[0]]:
                min_distance[row[0]] = dist
        return self.normalize_scores(min_distance,small_is_better=1)

    # 处理外部回指链接 在每个网页上统计链接的数目
    def inbound_link_score(self,rows):
        unique_urls = set([row[0] for row in rows])
        inbound_count = dict([(u,(self.cursor.execute("select count(*) from link where toid=%d"%u),self.cursor.fetchone()[0])[1]) for u in unique_urls])
        # print "inbound_count",inbound_count
        return self.normalize_scores(inbound_count)

    # 利用PageRank值进行归一化处理来进行评价
    def page_rank_score(self,rows):
        page_ranks = dict([(row[0],(self.cursor.execute("select score from pagerank where urlid=%d"%row[0]),
                                    self.cursor.fetchall()[0])[1]) for row in rows])
        max_rank = max(page_ranks.values())
        normalized_score = dict([(u,float(l) / max_rank) for (u,l) in page_ranks.items()])
        return normalized_score

    # 利用指向某一网页的链接文本来决定网页的相关度
    def link_text_socre(self,rows,word_ids):
        link_scores = dict([(row[0],0) for row in rows])
        for word_id in word_ids:
            self.cursor.execute("select link.fromid,link.toid from linkwords,link "
                                "where wordid=%d and linkwords.linkid=link.id"%word_id)
            for (fromid,toid) in self.cursor.fetchall():
                if toid in link_scores:
                    pr = (self.cursor.execute("select score from pagerank wher urlid=%d"%fromid),self.cursor.fetchone()[0])[1]
                    link_scores[toid] += pr
        max_score = max(link_scores.values())
        normalized_scores = dict([(u,float(l) / max_score) for (u,l) in link_scores.items()])
        return normalized_scores
if __name__ == '__main__':

    # page_list = ['http://en.people.cn/']
    craw = crawler()
    craw.calculate_page_rank()
    # craw.create_index_tables()
    # craw.crawl(page_list)
    # test = "insert into ss(id,ukr)VALUES (%d,%d)"%(1,2)
    # print test
    # l = [row for row in craw.cursor.execute('select * from wordlocation').fetchall()]
    # print l
    # searcher = Searcher()
    # print searcher.get_match_rows("test new party")

    # searcher.query("news china party test")




