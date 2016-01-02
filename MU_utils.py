# -*- coding: utf-8 -*-
import redis
import uuid
import logging
import logging.handlers
import os
import sys
import pdb
import re
import collections
os.chdir(os.path.dirname(sys.argv[0]))
r = redis.Redis(host="localhost", port=6379, db=0)
def unique_str():
    return str(uuid.uuid1())
def loggingInit(logname):
    isExists = os.path.exists('log')
    if not isExists:
        os.mkdir('log')
    LogExists = os.path.exists(logname)
    if not LogExists:
        f = open(logname, 'w')
        f.close()
    log = logging.getLogger(logname)
    log.setLevel(logging.DEBUG)
    logHandler = logging.handlers.RotatingFileHandler(logname,maxBytes=10*1024*1024,backupCount=5)
    logHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    logHandler.setFormatter(formatter)
    log.addHandler(logHandler)
    return log
def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv
def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv
def for_cat(dic):
    Categories = []
    if isinstance(dic, dict):
        key = dic['query']['pages'].keys()[0]
        value = dic['query']['pages'][key]
        for i in range(len(value['categories'])):
            Categories.append(value['categories'][i]['title'])
    return Categories
def for_rc(dic):
    #rc = []
    if isinstance(dic, collections.OrderedDict):
        key = dic['query'].keys()[0]
        value = dic['query'][key]
        #print type(value)
        #for i in range(len(value)):
            #rc.append(value[i]['title'])
    return value

