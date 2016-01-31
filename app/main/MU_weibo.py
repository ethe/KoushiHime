# -*- coding: utf-8 -*-
import sys
import redis
reload(sys)
import os
import urllib,urllib2,cookielib
import re,json
import base64,hashlib,rsa,binascii
os.chdir(os.path.dirname(__file__))
sys.setdefaultencoding('utf-8')
from weibo import APIClient
from MU_utils import r,_decode_dict
from MU_conf import MU_MainConfig

CALLBACK_URL='http://up.acggirl.moe'
REFERER='https://api.weibo.com/oauth2/authorize?redirect_uri=http%3A//up.acggirl.moe&response_type=code&client_id=563928974'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
headers = {'User-Agent':user_agent}
authheaders={'User-Agent':user_agent,'host':'api.weibo.com','method':'POST','content-type':'application/x-www-form-urlencoded','origin':'https://api.weibo.com'}
client=APIClient(app_key=MU_MainConfig.APP_KEY,app_secret=MU_MainConfig.APP_SECRET,redirect_uri=CALLBACK_URL)

def PrepareToken():
    read=client.request_access_token(MU_MainConfig.Code)
    access_token=read.access_token
    expires_in=read.expires_in
    r.set('access_token',access_token)
    r.expire('access_token',expires_in)
def PrepareLogin():
    access_token=r.get('access_token')
    expires_in=r.ttl('access_token')
    client.set_access_token(access_token, expires_in)
def post(status,pic):
    f=open(pic,'r')
    requesturl='https://api.weibo.com/2/short_url/shorten.json?access_token='+r.get('access_token')+'&url_long=http://zh.moegirl.org/'+urllib.quote(status)
    req=urllib2.Request(requesturl)
    res=urllib2.urlopen(req).read()
    data=json.loads(res,object_hook=_decode_dict)
    shorturl=data['urls'][0]['url_short']
    client.statuses.upload.post(status=status+shorturl,pic=f)
    f.close
