# -*- coding: utf-8 -*-
import sys
import redis
reload(sys)
import os
import urllib,urllib2,cookielib
import re,json
import base64,hashlib,rsa,binascii
os.chdir(os.path.dirname(sys.argv[0]))
sys.setdefaultencoding('utf-8')
from weibo import APIClient
from MU_utils import r,_decode_dict
APP_KEY='563928974'
APP_SECRET=''
CALLBACK_URL='http://up.acggirl.moe'
REFERER='https://api.weibo.com/oauth2/authorize?redirect_uri=http%3A//up.acggirl.moe&response_type=code&client_id=563928974'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
headers = {'User-Agent':user_agent}
authheaders={'User-Agent':user_agent,'host':'api.weibo.com','method':'POST','content-type':'application/x-www-form-urlencoded','origin':'https://api.weibo.com'}
Code=''
client=APIClient(app_key=APP_KEY,app_secret=APP_SECRET,redirect_uri=CALLBACK_URL)
regcallback='https%3A%2F%2Fapi.weibo.com%2F2%2Foauth2%2Fauthorize%3Fclient_id%3D563928974%26response_type%3Dcode%26display%3Ddefault%26redirect_uri%3Dhttp%253A%252F%252Fup.acggirl.moe%26from%3D%26with_cookie%3D'
redirecturi='http://up.acggirl.moe'
postdata={'cdult':'2','entry':'openapi','gateway':'1','from':'',"savestate":'0','userticket':'1','pagerefer':'','rsakv': '1330428213','prelt':'169','su': '','service': 'miniblog','servertime':'','nonce':'','pwencode':'rsa2','ct':'1800','encoding':'UTF-8','domain':'weibo.com','sp':'','returntype':'TEXT','vsnf':'1','s':"1"}
authpostdata={'action':'login','display':'default','withOfficalFlag':0,'quick_auth':'null','withOfficalAccount':'','scope':'','ticket':'','isLoginSina':'','response_type':'code','regCallback':regcallback,'redirect_uri':redirecturi,'client_id':APP_KEY,'appkey62':'Ugu6y','state':'','verifyToken':'null','from':'','switchLogin':0,'userid':'','passwd':''}

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
    pub_key = rsa.PublicKey(rsaPublickey, 65537)
    pwd = str(servertime)+'\t'+str(nonce)+'\n'+str(passwd)
    pwd1= rsa.encrypt(pwd, pub_key)
    pwd1=binascii.b2a_hex(pwd1)
    return pwd1
def LoginToWeibo():
    apiurl=client.get_authorize_url()
    authurl='https://api.weibo.com/oauth2/authorize'
    url='https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    #url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)'
    cj = cookielib.CookieJar()
    username=GetSu('')
    Secret=GetSecret()
    passwd=GetSp('',Secret[0],Secret[1])
    postdata['servertime']=Secret[0]
    postdata['nonce']=Secret[1]
    postdata['sp']=passwd
    postdata['su']=username
    form=urllib.urlencode(postdata)
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.HTTPHandler)
    opener.addheaders=[('User-agent',user_agent)]
    urllib2.install_opener(opener)
    req=urllib2.Request(url=url,data=form,headers=headers)
    result=urllib2.urlopen(req)
    text=result.read()
    #rep=json.loads(text)
    #ticket=rep['ticket']
    #authpostdata['ticket']=ticket
    #authform=urllib.urlencode(authpostdata)
    #authreq=urllib2.Request(url=authurl,data=authform,headers=authheaders)
    #authreq.get_method = lambda : 'HEAD'
    #authresult=urllib2.urlopen(authreq)
    #authtext=authresult.info()
    #print authtext
    p = re.compile('location\.replace\(\'(.*?)\'\)')
    try:
        login_url = p.search(text).group(1)
        print login_url
        urllib2.urlopen(login_url)
        print "登录成功!"
    except:
        print 'Login error!'
        
def GetCode(code):
    Code=code
def PrepareToken():
    Code='7581b56419b5ea52abc39c0f282716e6'
    read=client.request_access_token(Code)
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
    requesturl='https://api.weibo.com/2/short_url/shorten.json?access_token='+r.get('access_token')+'&url_long=http://zh.moegirl.org/'+status
    print requesturl
    req=urllib2.Request(requesturl.decode('utf-8').encode('gbk'))
    res=urllib2.urlopen(req).read()
    data=json.loads(res,object_hook=_decode_dict)
    print data
    shorturl=data['urls'][0]['url_short']
    client.statuses.upload.post(status=status+shorturl,pic=f)
    f.close
