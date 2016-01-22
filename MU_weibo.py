# -*- coding: utf-8 -*-
import sys
reload(sys)
import urllib,urllib2,cookielib
import re,json
import base64,hashlib,rsa,binascii
sys.setdefaultencoding('utf-8')
from weibo import APIClient
APP_KEY='563928974'
APP_SECRET=''
CALLBACK_URL='http://up.acggirl.moe'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0'
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
headers = {'User-Agent' : user_agent}
Code=''
client=APIClient(app_key=APP_KEY,app_secret=APP_SECRET,redirect_uri=CALLBACK_URL)
postdata={'cdult':'2','entry':'openapi','gateway':'1','from':'',"savestate":'0','userticket':'1','pagerefer':'','rsakv': '1330428213','prelt':'169','su': '','service': 'miniblog','servertime':'','nonce':'','pwencode':'rsa2','ct':'1800','encoding':'UTF-8','domain':'weibo.com','sp':'','returntype':'TEXT','vsnf':'1','s':"1"}

def GetSecret():
    se_url='http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=dW5kZWZpbmVk&client=ssologin.js(v1.3.18)&_=1329806375939'
    data = urllib2.urlopen(se_url).read()
    p = re.compile('\((.*)\)')
    try:
        json_data = p.search(data).group(1)
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        return servertime, nonce
    except:
        return None
def GetSu(username):
    username_ = urllib.quote(username)
    username=base64.encodestring(username_)[:-1]
    return username
def GetSp(passwd,servertime,nonce):
    #password=hashlib.sha1(passwd).hexdigest()
    #password1=hashlib.sha1(password).hexdigest()
    #password2=password1+servertime+nonce
    #password3=hashlib.sha1(password2).hexdigest()
    #return password3
    pubkey='EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
    rsaPublickey = int(pubkey, 16)
    pub_key = rsa.PublicKey(rsaPublickey, int('10001', 16))
    pwd = '%s\t%s\n%s' % (servertime, nonce,passwd)
    pwd1= rsa.encrypt(pwd, pub_key)
    pwd1=binascii.b2a_hex(pwd1)
    return pwd1
def LoginToWeibo():
    url=client.get_authorize_url()
    #url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)'
    cj = cookielib.CookieJar()
    username=GetSu('')
    Secret=GetSecret()
    passwd=GetSp('',Secret[0],Secret[1])
    postdata['servertime']=Secret[0]
    postdata['nonce']=Secret[1]
    postdata['su']=passwd
    postdata['sp']=username
    form=urllib.urlencode(postdata)
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders=[('User-agent',user_agent)]
    urllib2.install_opener(opener)
    req=urllib2.Request(url=url,data=form,headers=headers)
    result=urllib2.urlopen(req)
    text=result.read()
    p = re.compile('location\.replace\(\'(.*?)\'\)')
    #try:
    login_url = p.search(text).group(1)
        #print login_url
    #urllib2.urlopen(login_url)
    #print "登录成功!"
    #except:
     #   print 'Login error!'
        
def GetCode(code):
    Code=code
def PrepareToken():
    Code='5df64695bdcdb6f75f52235290ed3dba'
    read=client.request_access_token(code)
    access_token=read.access_token
    expires_in=read.expires_in
    client.set_access_token(access_token, expires_in)
def post(status,pic):
    f=open(pic,'r') 
    client.statuses.upload.post(status=status,pic=f)
    f.close
LoginToWeibo()
