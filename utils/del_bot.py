#!/usr/bin/env python3
import sys
import os
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'FFXIV.settings'
from FFXIV import settings
django.setup()
from ffxivbot.handlers.QQUtils import *
from asgiref.sync import async_to_sync
from ffxivbot.models import *
import re
import json
import time
import requests
import string
import random
import codecs
import urllib
import base64
import logging
from channels.layers import get_channel_layer
from django.db import connection, connections

def del_bot(day=7):
    bots = QQBot.objects.filter(event_time__lt=time.time()-3600*24*day)
    i = 0
    for b in bots:
        if int(b.user_id) in [2413448390,2521641680]:
            continue
        else:
            print("bot {} deleted".format(b))
            b.delete()
            i+=1
    print("{} bots del.".format(i))

if __name__ == "__main__":
    del_bot()
