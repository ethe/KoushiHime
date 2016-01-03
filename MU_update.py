# -*- coding: utf-8 -*-
import sys
reload(sys)
import datetime
import json
import urllib,urllib2
import calendar
import time
import os
from bs4 import BeautifulSoup
import logging,logging.handlers
import traceback
import weibo
from collections import OrderedDict
sys.setdefaultencoding('utf-8')
#from MU_conf import MUconf
from MU_utils import r,unique_str,loggingInit,for_cat,for_rc,_decode_dict
os.chdir(os.path.dirname(sys.argv[0]))
PUSHEDPREFIX="PUSHED-"
EDITEDPREFIX='EDITED-'
EXPIRETIME='72*3600'
log=loggingInit('log/update.log')
def GetCategory(title):
    apiurl="http://zh.moegirl.org/api.php"
    parmas = urllib.urlencode({'format':'json','action':'query','prop':'categories','titles':title})
    req=urllib2.Request(url=apiurl,data=parmas)
    res_data=urllib2.urlopen(req)
    ori=res_data.read()
    categories=json.loads(ori, object_hook=_decode_dict)
    cat=for_cat(categories)
    return cat
def GetImage(url):
    try:
        f=urllib.urlopen(url)
    except:
        return None
    src=f.read()
    f.close
    ssrc=BeautifulSoup(src,"html.parser")
    try:
        image_div=ssrc.find_all('a',class_='image')
        print type(image_div)
        for i in range(len(image_div)):
            imgtag=image_div[i].find('img')
            if (int(imgtag['width']) > 100 and int(imgtag['height']) > 200):
                img = imgtag['src']
                break
            else:
                continue
    except:
        return None
    isExists=os.path.exists('imgcache')
    if not isExists:
        os.makedirs('imgcache')
    name=unique_str()
    TheImageIsReadyToPush=False
    try:
        with open('imgcache/'+name,'wb') as f:
            con=urllib.urlopen(img)
            f.write(con.read())
            f.flush()
            TheImageIsReadyToPush=True
    except BaseException, e:
            log.debug(e)
            return None
    return TheImageIsReadyToPush
def ForbiddenItemsFilter(item):
    cat=GetCategory(item)
    ForCat="Category:屏蔽更新姬推送的条目"
    for i in range(len(cat)):
        if cat[i]==ForCat.encode('utf-8'):
            return False
            break
    return True
def ForbiddenItemPushed(title):
    for key in r.hkeys('queue'):
        if r.hget('queue',key)==PUSHEDPREFIX+title:
            return False
            break
    return True
class MU_UpdateData(object):
    def __init__(self):
        super(MU_UpdateData,self).__init__()
        self.cache=[]
        self.SendFlag=False
    def initupdater(self):
        self.GetRecentChanges(2)
    def GetRecentChanges(self):
        apiurl="http://zh.moegirl.org/api.php"
        format="%Y%m%d%H%M%S"
        utc=datetime.datetime.utcnow()
        rcstart=(utc-datetime.timedelta(hours=2)).strftime(format)
        rcend=utc.strftime(format)
        parmas=urllib.urlencode({'format':'json','action':'query','list':'recentchanges','rcstart':rcstart,'rcend':rcend,'rcdir':'newer','rcnamespace':'0','rctoponly':'','rctype':'edit|new','continue':''})
        req=urllib2.Request(url=apiurl,data=parmas)
        res_data=urllib2.urlopen(req)
        ori=res_data.read()
        rcc=json.loads(ori, object_hook=_decode_dict,object_pairs_hook=OrderedDict)
        value=for_rc(rcc)
        for i in range(len(value)):
            self.cache.append(value[i]['title'])
        return self.cache
    def FilterValid(self):
        self.GetRecentChanges()
        self.cache=filter(ForbiddenItemsFilter,self.cache)
        self.cache=filter(ForbiddenItemPushed,self.cache)
        return self.cache
    def SaveRecentChanges(self):
        self.FilterValid()
        for item in self.cache:
            itemkey=EDITEDPREFIX+item
            print itemkey
            r.hset('queue',itemkey,item)
            timenow=time.time()
            r.zadd('expire',itemkey,timenow)
    def RemoveExpiredItems(self):
        r.zrange('expire',0,-1)
        
item='123'
update=MU_UpdateData()
v=update.SaveRecentChanges()
print v
