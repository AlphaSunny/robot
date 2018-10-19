from wxpy import *
import json
import requests
import datetime, time
from urllib import parse
from urllib import request
import os
import oss2
# import hashlib
# import random
# import base64
import threading


# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
# auth = oss2.Auth('LTAIuZaZnZxBZzUK', 'beGtC3IxwuftzW2aSubRP1STNVbAUH')
# # Endpoint以杭州为例，其它Region请按实际情况填写。
# bucket_name = 'pythonccvt'
# aliyun_url = 'oss-cn-hongkong.aliyuncs.com'
# bucket = oss2.Bucket(auth, aliyun_url, bucket_name)
# img_key = 'img/img.png'
# img_path = '../static/abc.png'
# result = bucket.put_object_from_file(img_key, img_path)
#
# url = bucket_name+"."+aliyun_url+"/"+img_key
#
#
# print(url)

