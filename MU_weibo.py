# -*- coding: utf-8 -*-
import sys
reload(sys)
import urllib,urllib2
from  lxml.html.soupparser as soupparser
sys.setdefaultencoding('utf-8')
from weibo import APIClient
APP_KEY='563928974'
APP_SECRET=''
CALLBACK_URL='http://up.acggirl.moe'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0'
headers = {'User-Agent' : user_agent}
Code=''
client=APIClient(app_key=APP_KEY,app_secret=APP_SECRET,redirect_uri=CALLBACK_URL)
def LoginToWeibo():
    url=client.get_authorize_url()
    res_data=urllib2.urlopen(url)

def GetCode(code):
    Code=code
def PrepareToken():
    Code=''
    read=client.request_access_token(code)
    access_token=read.access_token
    expires_in=read.expires_in
    client.set_access_token(access_token, expires_in)
def post(status,pic):
    f=open(pic,'r') 
    client.statuses.upload.post(status=status,pic=f)
    f.close
LoginToWeibo()