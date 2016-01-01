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

#from MU_conf import MUconf
from MU_utils import r,unique_str,loggingInit,for_dict
queue=[]
os.chdir(os.path.dirname(sys.argv[0]))
log=loggingInit('log/update.log')
def GetCategory(title):
    apiurl="http://zh.moegirl.org/api.php"
    parmas = urllib.urlencode({'format':'json','action':'query','prop':'categories','titles':title})
    req=urllib2.Request(url=apiurl,data=parmas)
    res_data=urllib2.urlopen(req)
    ori=res_data.read()
    categories=json.loads(ori)
    for_dict(categories)
    return categories
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
            print imgtag
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

class MU_UpdateData:
    def __enter__(self):
        return self
    def __exit__(self,type,value,traceback):
        log.debug('value:%s,traceback:%s' %value,traceback)
