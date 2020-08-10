from .QQEventHandler import QQEventHandler
from .QQUtils import *
from ffxivbot.models import *
import logging
import json
import random
import requests
import traceback
import time
import copy
import re
import os
from bs4 import BeautifulSoup


def get_image_from_CQ(CQ_text):
    if "url=" in CQ_text:
        tmp = CQ_text
        tmp = tmp[tmp.find("url=") : -1]
        tmp = tmp.replace("url=", "")
        img_url = tmp.replace("]", "")
        return img_url
    return None


    if token:
        headers = {"Authorization":token}
    original_image = requests.get(url=img_url, timeout=5)
    sm_req = requests.post(
        headers=headers, url="https://sm.ms/api/v2/upload", files={"smfile": original_image.content}, timeout=30
    )
    return json.loads(sm_req.text)


def delete_image(img_hash):
    sm_req = requests.post(url="https://sm.ms/api/v2/delete/{}".format(img_hash), timeout=5)
    return sm_req.status_code

def tata_tuku():
    tata_login = "https://xn--v9x.net/login/"
    tata_re = requests.get(tata_login)
    login_csrf =  re.search(r"value=\"(.*)?\"",tata_re.text)[1]
    payload = {'Email': '952547082@qq.com',
               'Password': '112233',
               'csrfmiddlewaretoken': login_csrf}
    aheaders = {'Content-Type': 'application/x-www-form-urlencoded', 'cookie': 'csrftoken={}'.format(login_csrf), 'refer': 'https://xn--v9x.net/login/'}
    tata_re = requests.post(url=tata_login, data=payload, headers=aheaders, allow_redirects=False)
    ck = "{}={};{}={}".format(tata_re.cookies.items()[0][0],tata_re.cookies.items()[0][-1],tata_re.cookies.items()[1][0],tata_re.cookies.items()[1][-1])
    csrftoken = tata_re.cookies.items()[0][-1]
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tuku.txt"),"w") as l:
        l.write("{}\n{}\n{}".format(time.strftime("%Y-%m-%d",time.localtime()),csrftoken,ck))
        l.close()
    return [csrftoken,ck]

def QQCommand_image(*args, **kwargs):
    action_list = []
    try:
        global_config = kwargs["global_config"]
        QQ_BASE_URL = global_config["QQ_BASE_URL"]
        SMMS_TOKEN = global_config.get("SMMS_TOKEN", "")
        receive = kwargs["receive"]

        receive_msg = receive["message"].replace("/image", "", 1).strip()
        msg_list = receive_msg.split(" ")
        second_command = msg_list[0]
        if second_command == "" or second_command == "help":
        elif second_command == "upload":
            if len(msg_list) < 3:
                msg = "您输入的参数个数不足：\n/image upload $category $image : 给类别$category上传图片"
            else:
                (qquser, created) = QQUser.objects.get_or_create(
                    user_id=receive["user_id"]
                )
                if not qquser.able_to_upload_image:
                    msg = "[CQ:at,qq={}] 您由于触犯规则无权上传图片".format(receive["user_id"])
                else:
                    category = msg_list[1].strip()
                    CQ_text = msg_list[2].strip()
                    img_url = get_image_from_CQ(CQ_text)
                    if not img_url:
                        msg = "未发现图片信息"
                    else:
                        img_info = upload_image(img_url, SMMS_TOKEN)
                        if not img_info["success"]:
                            print("img_info:{}".format(json.dumps(img_info)))
                            msg = img_info["message"]
                            if "Image upload repeated limit, this image exists at: " in msg:
                                url = msg.replace("Image upload repeated limit, this image exists at: ", "")
                                path = url.replace("https://i.loli.net", "")
                                path = path.replace("https://vip1.loli.net", "")
                                domain = "https://vip1.loli.net" if "https://vip1.loli.net" in url else "https://i.loli.net"
                                name = copy.deepcopy(path)
                                while "/" in name:
                                    name = name[name.find("/")+1:]
                                try:
                                    img = Image.objects.get(path=path)
                                    msg = '图片"{}"已存在于类别"{}"之中，无法重复上传'.format(img.name, img.key)
                                except Image.DoesNotExist:
                                    img = Image(
                                        domain=domain,
                                        key=category,
                                        name=name,
                                        path=path,
                                        img_hash="null",
                                        timestamp=int(time.time()),
                                        add_by=qquser,
                                    )
                                img.save()
                                msg = '图片"{}"上传至类别"{}"成功'.format(img.name, img.key)
                        else:
                            img_info = img_info["data"]
                            url = img_info.get("url", "")
                            domain = "https://vip1.loli.net" if "https://vip1.loli.net" in url else "https://i.loli.net"
                            img = Image(
                                domain=domain,
                                key=category,
                                name=img_info["storename"],
                                path=img_info["path"],
                                img_hash=img_info["hash"],
                                timestamp=img_info.get("timestamp", 0),
                                url=url,
                                add_by=qquser,
                            )
                            img.save()
                            msg = '图片"{}"上传至类别"{}"成功'.format(img.name, img.key)
        elif second_command == "del":
            if len(msg_list) < 2:
                msg = "您输入的参数个数不足：\n/image del $name : 删除名为$name的图片"
            else:
                name = msg_list[1].strip()
                (qquser, created) = QQUser.objects.get_or_create(
                    user_id=receive["user_id"]
                )
                imgs = Image.objects.filter(name=name, add_by=qquser)
                if not imgs.exists():
                    msg = '未找到名为"{}"的图片或您无权删除这张图片'.format(name)
                else:
                    for img in imgs:
                        img.delete()
                    msg = '图片"{}"删除完毕'.format(name)
        else:
            if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "text/tuku.txt")):
                g = []
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "text/tuku.txt"),"r") as l:
                    for line in l.readlines():
                        line = line.strip('\n')
                        g.append(line)
                    l.close()
                if g[0] < time.strftime("%Y-%m-%d",time.localtime()):
                    tata = tata_tuku()
                else:
                    tata = [g[1],g[2]]
            else:
                tata = tata_tuku()

            taurl = 'https://xn--v9x.net/image/'
            category = msg_list[0].strip()
            get_info = "info" in category
            j = True
            category = category.replace("info", "", 1)
            imgs = Image.objects.filter(key=category)
            try:
                headers = {'X-csrftoken':tata[0],'X-Requested-With':'XMLHttpRequest','Cookie':tata[1],'Referer':'https://xn--v9x.net/image/'}
                jdata = json.dumps({
                                    "optype":"get_images",
                                    "category":category,
                                    "cached_images":[]
                                    })
                gr = requests.post(url=taurl,headers=headers,data=jdata,timeout=5)
                gimage = gr.json()
            except:
                gimage = {"images":[]}

            if not imgs.exists() and gimage["images"]==[]:
                msg = '未找到类别"{}"的图片'.format(category)
            else:
                if not imgs.exists():
                    imgs = []
                img = random.sample(list(imgs)+gimage["images"], 1)[0]
                if isinstance(img,dict):
                    msg = "[CQ:image,cache=0,file={}]\n".format(
                        img["url"]
                    )
                    if get_info:
                        msg += "{}".format(img["info"])
                else:
                    msg = "[CQ:image,cache=0,file={}]\n".format(
                        img.domain + img.path
                    )
                    if get_info:
                        msg += "{}\nCategory:{}\nUploaded by:{}\n".format(
                            img.name, img.key, img.add_by
                        )
        msg = msg.strip()
        reply_action = reply_message_action(receive, msg)
        action_list.append(reply_action)
        return action_list
    except Exception as e:
        msg = "Error: {}".format(type(e))
        action_list.append(reply_message_action(receive, msg))
        logging.error(e)
        traceback.print_exc()
    return action_list