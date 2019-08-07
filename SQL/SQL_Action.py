'''
Created on 2019年2月22日

@author: Administrator
'''
import pymysql
import traceback
  

# from DBUtils.PooledDB import PooledDB
class SQL_ACTION(object):
    '''
    sql操作
    '''
    address = 'localhost'
    username = 'root'
    password = '12345678'
    databasename = 'caoliu'
    charset = 'utf-8'
    pool = None
    limit_cnt = 3

    # 设置数据库链接
    # db=pymysql.connect(address,username,password,databasename)
    def __init__(self, params):
        '''
        Constructor
        '''
        # self.pool=PooledDB(pymysql,self.limit_cnt,host=self.address,user=self.username,passwd=self.password,
        # db=self.databasename,port=3306,charset=self.charset,use_unicode=True)

    # 执行sql语句
    def ExcuteSQL(self, sql, T):
        # 设置数据库链接
        db = pymysql.connect(self.address, self.username, self.password, self.databasename)
        # 设置游标
        cursor = db.cursor()
        # sql='insert into %s (type,title,link) values (%s,%s,%s)'
        try:
            # 执行
            cursor.executemany(sql, T)
            # 提交
            db.commit()
            print('执行成功')
        except:
            # 回滚
            traceback.print_exc()
            db.rollback()
        db.close()

    # 执行sql语句
    '''
    def ExcuteSql(self,sql):
        #设置数据库链接
        #self.db=pymysql.connect(address,username,password,databasename)
        #设置游标
        cursor=self.db.cursor()
        print(sql)
        try:
            #执行
            cursor.execute(sql)
            #提交
            self.db.commit()
            print('执行成功')
        except:
            #回滚
            traceback.print_exc()  
            self.db.rollback()
        self.db.close()
    '''

    # 获取数据集
    def GetQuery(self, sql):
        db = pymysql.connect(self.address, self.username, self.password, self.databasename)
        # 设置游标
        cursor = db.cursor()
        print(sql)
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            print('获取数据集成功')
            return results
        except:
            # 回滚
            traceback.print_exc()
            db.rollback()
        db.close()


