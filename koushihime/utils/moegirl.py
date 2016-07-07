# -*- coding: utf-8 -*-

import re
import os
import json
from hashlib import md5
from collections import OrderedDict
from datetime import datetime, timedelta
from urllib import urlencode
from urllib2 import Request, urlopen
from bs4 import BeautifulSoup
from flask import current_app
from . import _decode_dict
from koushihime.main.models import BanList


class MoegirlQuery(object):

    def __init__(self, title):
        self.title = title
        self.api_url = current_app.config["MOEGIRL_API_ROOT"]
        self.params = {'format': 'json', 'action': 'query',
                       'prop': 'categories', 'titles': title}
        self.response = None

    def request(self, **attach_param):
        if attach_param:
            self.params.update(attach_param)
        encode_params = urlencode(self.params)
        request = Request(url=self.api_url, data=encode_params)
        response_object = urlopen(request)
        json_response = response_object.read()
        self.response = json.loads(json_response, object_hook=_decode_dict)
        return self.response

    def get_categories(self):
        categories = []
        response = self.response if self.response else self.request()
        if isinstance(response, dict):
            key = response['query']['pages'].keys()[0]
            value = response['query']['pages'][key]
            try:
                for i in range(len(value['categories'])):
                    categories.append(value['categories'][i]['title'])
            except:
                pass
        return categories

    def banned_moegirl_category(self):
        cat = self.get_categories()
        banned = u"Category:屏蔽更新姬推送的条目"
        for i in range(len(cat)):
            if cat[i] == banned.encode('utf-8'):
                return True
        return False

    def get_namespace(self):
        response = self.response if self.response else self.request()
        response_odict = OrderedDict(response)
        if response['query']['pages'].keys()[0] is not '-1':
            key = response_odict['query']['pages'].keys()[0]
            namespace = response_odict['query']['pages'][key]['ns']
            return namespace
        return None

    def ban_from_regex(self):
        regex_list = BanList.query.all()
        if regex_list:
            for rule_object in regex_list:
                rule = rule_object.rule
                if 'Category:' not in rule:
                    if re.search(rule, self.title.decode("utf-8")):
                        if rule_object.status.count == 0:
                            return True
                        else:
                            self.fresh_rule_push_count(rule_object)
                else:
                    categories = self.get_categories()
                    for category in categories:
                        if re.search(rule[len("Category"):].split(' ')[-1], category):
                            if rule_object.status.count == 0:
                                return True
                            else:
                                self.fresh_rule_push_count(rule_object)
        return False

    @staticmethod
    def fresh_rule_push_count(rule_object):
        rule_object.status.count -= 1
        rule_object.save()


class MoegirlImage(object):

    def __init__(self, title):
        self.path_root = "./koushihime/imgcache"
        try:
            self.url = "https://zh.moegirl.org/" + title.encode('utf-8')
        except:
            self.url = "https://zh.moegirl.org/" + title
        self.touch_cache_folder()
        self.raw_bytes = self.get_image()
        self.hash = self.image_hash()
        self.path = self.save_image()
        self.raw_bytes = lambda: open(self.path, 'rb') if self.path else None

    def image_hash(self):
        if self.raw_bytes:
            hash_object = md5(self.raw_bytes)
            return hash_object.hexdigest()
        return ''

    def get_image(self):
        image_file = urlopen(self.url)
        raw_html = image_file.read()
        ssrc = BeautifulSoup(raw_html, "html.parser")
        image_url = None
        try:
            image_div = ssrc.find_all('a', class_='image')
            for image in image_div:
                imgtag = image.find('img')
                if (int(imgtag['width']) > 200 and int(imgtag['height']) > 100):
                    image_url = imgtag['src']
                    break
        except:
            return None
        if image_url:
            self.type = image_url.split('.')[-1]
            try:
                headers = self.cloudflare_headers
                request = Request(url=image_url, headers=headers)
                image = urlopen(request)
                image_bytes = image.read()
            except:
                return None
        else:
            return None
        return image_bytes

    def save_image(self):
        if self.raw_bytes and self.hash:
            try:
                file_path = "{}/{}.{}".format(self.path_root, self.hash, self.type)
                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as f:
                        f.write(self.raw_bytes)
                        f.flush()
                return file_path
            except:
                return None
        return None

    def touch_cache_folder(self):
        is_exists = os.path.exists(self.path_root)
        if not is_exists:
            os.makedirs(self.path_root)

    @property
    def cloudflare_headers(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.6,en;q=0.4",
            "cache-control": "max-age=0",
            "cookie": "__cfduid=dfc6b63939d0f061541f2368f5233734b1461485677",
            "if-none-match": "56a5edcc-8cb9",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
        }
        return headers


def get_recent_changes():
    apiurl = "https://zh.moegirl.org/api.php"
    date_format = "%Y%m%d%H%M%S"
    utc = datetime.utcnow()
    rcstart = (utc - timedelta(hours=1)).strftime(date_format)
    rcend = utc.strftime(date_format)
    parmas = urlencode({'format': 'json', 'action': 'query', 'list': 'recentchanges', 'rcstart': rcstart, 'rcend': rcend,
                               'rcdir': 'newer', 'rcnamespace': '0', 'rctoponly': '', 'rctype': 'edit|new', 'continue': '',
                               'rcprop': 'title|sizes'})
    req = Request(url=apiurl, data=parmas)
    res_data = urlopen(req)
    ori = res_data.read()
    change_query = json.loads(ori, object_hook=_decode_dict)
    change_list = change_query['query']['recentchanges']
    return change_list
