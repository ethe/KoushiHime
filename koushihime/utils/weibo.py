# -*- coding: utf-8 -*-
import json
import gzip
import time
import requests
import mimetypes
import urllib2
from StringIO import StringIO


class WeiboAPI(object):

    headers = {'Accept': 'application/json, text/plain, */*',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6,en;q=0.4',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest',
               'Host': 'm.weibo.cn',
               'Origin': 'https://m.weibo.cn',
               'Referer': 'https://m.weibo.cn/compose'}
    upload_path = 'https://m.weibo.cn/api/statuses/uploadPic'
    post_path = 'https://m.weibo.cn/api/statuses/update'

    def __init__(self, cookie):
        self.headers['Cookie'] = cookie

    def upload_image(self, image):
        params, boundary = self.encode_body(**{'type': 'json', 'st': self.st, 'pic': image})
        req = urllib2.Request(self.upload_path, headers=self.headers, data=params)
        req.add_header('Content-Type', 'multipart/form-data; boundary={}'.format(boundary))
        return json.loads(self.read_body(urllib2.urlopen(req)))

    def post(self, content, pic=None):
        data = {'content': content, 'st': self.st}
        if pic:
            data['picId'] = pic
        resp = requests.post(self.post_path, headers=self.headers, data=data)
        try:
            return resp.json()
        except:
            raise WeiboPostError(resp.text)

    @property
    def st(self):
        return requests.get(
            "https://m.weibo.cn/api/config", headers=self.headers).json()['st']

    def encode_body(self, **kw):
        ' build a multipart/form-data body with randomly generated boundary '
        boundary = '----------{}'.format(hex(int(time.time() * 1000)))
        data = []
        for k, v in kw.iteritems():
            data.append('--{}'.format(boundary))
            if hasattr(v, 'read'):
                # file-like object:
                filename = getattr(v, 'name', '')
                content = v.read()
                data.append('Content-Disposition: form-data; name="{}"; filename="{}"'.format(k, filename))
                data.append('Content-Length: {}'.format(len(content)))
                data.append('Content-Type: {}\r\n'.format(self.guess_content_type(filename)))
                data.append(content)
            else:
                data.append('Content-Disposition: form-data; name="{}"\r\n'.format(k))
                data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
        data.append('--{}--\r\n'.format(boundary))
        return '\r\n'.join(data), boundary

    @staticmethod
    def guess_content_type(url):
        n = url.rfind('.')
        if n == (-1):
            return 'application/octet-stream'
        ext = url[n:]
        return mimetypes.types_map.get(ext, 'application/octet-stream')

    @staticmethod
    def read_body(req):
        using_gzip = req.headers.get('Content-Encoding', '') == 'gzip'
        body = req.read()
        if using_gzip:
            gzipper = gzip.GzipFile(fileobj=StringIO(body))
            fcontent = gzipper.read()
            gzipper.close()
            return fcontent
        return body


class WeiboPostError(Exception):
    pass
