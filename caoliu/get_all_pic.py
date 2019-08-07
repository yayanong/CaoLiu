'''
Created on 2019年2月22日

@author: Administrator
'''
from caoliu.get_title_list import get_title_list

if __name__ == '__main__':
    gtl=get_title_list(1)
    #gtl.get_List('https://cc.wuel.icu/thread0806.php?fid=16&search=&page=', '达盖尔的旗帜')
    #gtl.get_List('https://cc.wuel.icu/thread0806.php?fid=8&search=&page=', '新時代的我們')
    gtl.get_pic()
    pass