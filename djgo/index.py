from django.shortcuts import render_to_response
# import djgo.sel_bot
from djgo.robot import Robot
import os
import oss2
import random
import hashlib
from urllib import parse
from urllib import request
import djgo.common as a

from wxpy import *

url = a.url()

def index(request):
    return render_to_response('index.html')

def show_uuid(uuid, status, qrcode):
    address = "./static/"+get_guid()+".png"
    with open(address, "wb") as f:
        f.write(qrcode)

    #上传到阿里云
    path = oss_upload('qr_img/' + get_guid() + ".jpg", address)

    # 删除本地图片
    os.remove(address)


    params = parse.urlencode({'qrcode': path})
    url_path = url + "/bot/bot_qrcode.php?%s" % params

    request.urlopen(url_path)


def search(request):

    bot = Bot(console_qr=True, cache_path=True, qr_callback=show_uuid)

    rot = Robot(bot)
    rot.send_to_message()


    embed()

    return render_to_response('index.html')


#上传到阿里云
def oss_upload(img_key, img_path):
    accessKeyId = 'LTAIuTfkvjnNg54j'
    accessKeySecret = 'OTETap8a971xgfYdNCawWuHTkbR5dj'
    bucket_name = 'ccvthb'
    aliyun_url = 'oss-cn-beijing.aliyuncs.com'
    auth = oss2.Auth(accessKeyId, accessKeySecret)
    bucket = oss2.Bucket(auth, aliyun_url, bucket_name)
    bucket.put_object_from_file(img_key, img_path)
    url = "http://" + bucket_name+"."+aliyun_url+"/"+img_key
    return url

#生成唯一值
def get_guid():
    seed = "1234567890abcdefghijklmnopqrstuvwxyz"
    sa = []
    for i in range(12):
        sa.append(random.choice(seed))
    salt = ''.join(sa)

    hash = hashlib.md5()
    hash.update(salt.encode())
    md5ha = hash.hexdigest()
    return md5ha


def set_json(request):
    # djgo.sel_bot.set_json()
    print(1222)




