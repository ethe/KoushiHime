# -*- coding: utf-8 -*-

import json
from collections import OrderedDict
from urllib2 import urlencode, Request, urlopen
from flask import current_app
from . import _decode_dict


class MoegirlQuery(object):

    def __init__(self, title):
        self.title = title
        self.api_url = current_app.cofig["MOEGIRL_API_ROOT"]
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
