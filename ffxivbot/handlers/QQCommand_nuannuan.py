from .QQEventHandler import QQEventHandler
from .QQUtils import *
from ffxivbot.models import *
import logging
import json
import random
import requests
import os
import io
import time
import base64
from PIL import ImageFont,Image,ImageDraw


def msg_to_img(msg,n=3):
    g = 35 * n
    text = u"{}".format(msg)
    im = Image.new("RGB", (1300,g),(250,250,250))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), "arknights/fonts/msyh.ttc"), 28)
    dr.text((10, 10), text, font=font, fill="#1B1B1B")
    output_buffer = io.BytesIO()
    im.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode("utf-8")
    rc = "[CQ:image,file=base64://{}]".format(base64_str)
    return rc

def get_data():
    try:
        msg = "第{}周时尚品鉴攻略\n---\n"
        keyword =   {   'week':'21','theme':'38',
                        'tag1':'65','con1':'114',
                        'tag2':'161','con2':'210',
                        'tag3':'257','con3':'306',
                        'tag4':'369','con4':'418'
                    }
        url = "https://docs.qq.com/dop-api/opendoc?tab=dewveu&id=DY2lCeEpwemZESm5q&outformat=1&normal=1&startrow=0&endrow=60&wb=1&nowb=0"
        r = requests.get(url=url, timeout=10)
        result = r.json()
        result = result['clientVars']['collab_client_vars']['initialAttributedText']['text'][0][5][0]['c'][1]
        rc = msg.format(result[keyword['week']]['2'][-1])+ \
            "本周主题【{}】\n---\n".format(result[keyword['theme']]['2'][-1])+ \
            "【{}】:\n".format(result[keyword['tag1']]['2'][-1])+ \
            "{}\n".format(result[keyword['con1']]['2'][-1])+ \
            "【{}】:\n".format(result[keyword['tag2']]['2'][-1])+ \
            "{}\n".format(result[keyword['con2']]['2'][-1])+ \
            "【{}】:\n".format(result[keyword['tag3']]['2'][-1])+ \
            "{}\n".format(result[keyword['con3']]['2'][-1])+ \
            "【{}】:\n".format(result[keyword['tag4']]['2'][-1])+ \
            "{}\n---\n".format(result[keyword['con4']]['2'][-1])+ \
            "攻略来源-B站@游玩C哩酱，个人主页：https://www.youwanc.com/"
    except:
        url = "https://docs.qq.com/dop-api/opendoc?tab=BB08J2&id=DY2lCeEpwemZESm5q&outformat=1&normal=1&startrow=0&endrow=60&wb=1&nowb=0"
        r = requests.get(url=url, timeout=10)
        result = r.json()
        result = result['clientVars']['collab_client_vars']['initialAttributedText']['text'][0][4][0]['c'][1]
        tags=['头部防具','身体防具','手部防具','腿部防具','脚部防具','耳坠','项环','手饰','戒指']
        tag_keys=[]
        cons=[]

        keywords = list(result.keys())
        for i in keywords:
            if '2' in result[i].keys():
                if '最新期' in str(result[i]['2'][-1]):
                    nn_key = i
                    break
                else:
                    continue
            else:
                continue

        for i in range(3,12):
            if '2' in result[str(int(nn_key)+i)].keys() and not result[str(int(nn_key)+i)]['2'][-1].isspace():
                cons.append(result[str(int(nn_key)+i)]['2'][-1])
                tag_keys.append(i-3)
            else:
                continue
        rc = "时尚品鉴预测攻略\n---\n"+ \
            "【{}】:\n".format(tags[tag_keys[0]])+ \
            "{}\n".format(cons[0])+ \
            "【{}】:\n".format(tags[tag_keys[1]])+ \
            "{}\n".format(cons[1])+ \
            "【{}】:\n".format(tags[tag_keys[2]])+ \
            "{}\n".format(cons[2])+ \
            "【{}】:\n".format(tags[tag_keys[3]])+ \
            "{}\n---\n".format(cons[3])+ \
            "攻略来源-B站@游玩C哩酱，个人主页：https://www.youwanc.com/"
    return rc

def QQCommand_nuannuan(*args, **kwargs):
    action_list = []
    try:
        QQ_BASE_URL = kwargs["global_config"]["QQ_BASE_URL"]
        receive = kwargs["receive"]
        bot = kwargs["bot"]
        bot_version = (json.loads(bot.version_info)["coolq_edition"].lower()
                       if bot.version_info != '{}'
                       else "pro")
        nn_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'nn.json')
        if not os.path.exists(nn_path):
            nn = open(nn_path, 'w').write('{"date":0,"img":"","text":""}')
        nn = json.loads(open(nn_path).read())
        if int(time.time())-nn['date'] > 3600:
            text = get_data()
            img = msg_to_img(text,text.count("\n")+1)
            nn['img'] = img
            nn['text'] = text
            nn['date'] = int(time.time())
            nn = open(nn_path, 'w').write(json.dumps(nn))
            nn = json.loads(open(nn_path).read())
        if bot_version == "air" or "text" in receive["message"]:
            msg = nn['text']
        else:
            msg = nn['img']
        reply_action = reply_message_action(receive, msg)
        action_list.append(reply_action)
    except Exception as e:
        if "KeyError" in e:
            msg = "本周时尚品鉴攻略暂未公布"
        else:
            msg = "Error: {}".format(type(e))
        action_list.append(reply_message_action(receive, msg))
        logging.error(e)
    return action_list