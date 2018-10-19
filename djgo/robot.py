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



url = "http://ccvt_test.fnying.com/api"

class Robot(object):
    def __init__(self, bot):
        self.bot = bot

    #聊天
    def send_to_message(self):

        # 生成本地group json文件，因为下面的进程会卡死，所以先生成一次
        self.set_group_json_first()

        #个人图灵机器人
        self.sel_this_day_info()

        #群聊图灵机器人
       # self.start_record_bot()

        # 收集群聊信息
        group_list = self.get_group_json()
        for name in group_list:
            self.start_record_bot(name['name'])


        #循环调用接口生成json,循环调用json判断时间
        #注：不能写t1 = threading.Thread(target=self.set_timer())
        threads = []
        t1 = threading.Thread(target=self.set_timer)
        threads.append(t1)
        t2 = threading.Thread(target=self.timer_run)
        threads.append(t2)
        t3 = threading.Thread(target=self.judge_group_or_same)
        threads.append(t3)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    # 每30秒判断一次接口最新数据库与本地生成的json是否相同，不同的数据，生成群聊对象
    def judge_group_or_same(self):
        while True:
            data = request.urlopen(url + "/bot/get_group.php").read()
            data_json = json.loads(data.decode("utf-8"))
            dict = data_json['rows']
            # dumps 将数据转换成字符串
            json_str = json.dumps(dict)

            # loads: 将 字符串 转换为 字典
            dict2 = json.loads(json_str)

            dict1 = self.get_group_json()
            id = []
            name = []
            ba_id = []
            for i in dict1:
                id.insert(0, i['id'])
                name.insert(0, i['name'])
                ba_id.insert(0, i['ba_id'])

            for a in dict2:
                if (a['id'] not in id) or (a['name'] not in name) or (a['ba_id'] not in ba_id):
                    self.start_record_bot(a['name'])

            #更新json文件
            self.set_group_json_first()

            time.sleep(30)

    # 调用group接口，生成本地json文件
    def set_group_json_first(self):
        data = request.urlopen(url + "/bot/get_group.php").read()
        data_json = json.loads(data.decode("utf-8"))
        dict = data_json['rows']
        # dumps 将数据转换成字符串
        json_str = json.dumps(dict)

        # loads: 将 字符串 转换为 字典
        new_dict = json.loads(json_str)
        # print(new_dict)

        with open("./json/group.json", "w") as f:
            json.dump(new_dict, f)

    # 读取本地group文件内容
    def get_group_json(self):
        with open("./json/group.json", 'r') as load_f:
            load_dict = json.load(load_f)
            return load_dict



    #每秒定时循环本地json文件内容
    def timer_run(self):
        while True:
            # 取出date.json内容
            dat = self.get_date()
            a = time.localtime()
            week = time.strftime("%A", a)
            date_of = datetime.datetime.now().strftime('%Y-%m-%d')
            da = []
            for i in dat:
                da.insert(0, i['date'])

            if (week not in da) or (date_of not in da):

                group_list = self.get_group_json()
                for name in group_list:
                    groups = self.bot.groups()
                    group = groups.search(name['name'])[0]
                    now = datetime.datetime.now()
                    rows = self.get_timer()
                    for i in rows:
                        h = int(i['time'].split(":")[0])
                        m = int(i['time'].split(":")[1])
                        # s = int(i['time'].split(":")[-1])
                        # print(h, m, s)
                        if now.hour == h and now.minute == m and name['id'] == i['group_id'] and int(name['is_del']) == 1:
                            if now.hour == 22:
                                params = parse.urlencode({'group_name': name['name']})
                                data = request.urlopen(url+"/bot/search_chat.php?%s" % params).read()
                                data_json = json.loads(data.decode("utf-8"))
                                content = i['content'] + "，今日聊天记录查看地址:" + data_json['url']
                            else:
                                content = i['content']

                            group.send(content)
                            break
            time.sleep(60)


    #调用接口循环判断
    def set_timer(self):
        while True:
            data = request.urlopen(url+"/bot/timer.php").read()
            data_json = json.loads(data.decode("utf-8"))
            dict = data_json['rows']
            # dumps 将数据转换成字符串
            json_str = json.dumps(dict)

            # loads: 将 字符串 转换为 字典
            new_dict = json.loads(json_str)
            # print(new_dict)

            with open("./json/timer.json", "w") as f:
                json.dump(new_dict, f)

            # 循环日期或周几生成本地文件
            d = request.urlopen(url+"/bot/get_date.php").read()
            d_json = json.loads(d.decode("utf-8"))
            dict2 = d_json['rows']
            # dumps 将数据转换成字符串
            json_str2 = json.dumps(dict2)

            # loads: 将 字符串 转换为 字典
            new_dict2 = json.loads(json_str2)
            # print(new_dict2)

            with open("./json/date.json", "w") as f:
                json.dump(new_dict2, f)

            # 每60秒调一次接口
            time.sleep(60)


    #取出本地json文件内容
    def get_timer(self):
        with open("./json/timer.json", 'r') as load_f:
            load_dict = json.load(load_f)
            return load_dict

    # 取出本地date.json文件内容
    def get_date(self):
        with open("./json/date.json", 'r') as load_f:
            load_dict = json.load(load_f)
            return load_dict


    # 收集群聊信息
    #lstrip :从字符串左侧删除
    def start_record_bot(self, name):
       record_group = self.bot.groups().search(name)[0]
       @self.bot.register(record_group)
       def forward_boss_message(msg):
           #print(msg.raw)

           gr = self.get_group_json()
           for g in gr:

               # 判断群功能是否打开
               if name == g['name'] and int(g['is_del']) == 1:

                   try:
                       my_friend = self.bot.friends().search(msg.raw['ActualNickName'])[0]
                       path = "./static/" + msg.raw['ActualNickName'] + ".jpg"
                       my_friend.get_avatar(path)

                       #上传到阿里云
                       path = self.oss_upload('img/'+msg.raw['ActualNickName']+".jpg", path)

                       #删除本地图片
                       os.remove(path)

                   except:
                       path = ''

                   #如果是视频或者图片，下载图片，视频
                   if msg.raw['Type'] == "Picture" or msg.raw['Type'] == "Video" or msg.raw['Type'] == "Recording":
                       t = "./static/" + msg.raw['FileName']
                       msg.get_file(t)        #下载图片，视频

                       # 上传到阿里云
                       content = self.oss_upload('img/' + msg.raw['FileName'], t)

                       #删除本地文件
                       os.remove(t)


                   else:
                       content = msg.text


                   # 插入数据库
                   self.insert_message(msg.raw['CreateTime'], msg.raw['ActualNickName'], content, g['ba_id'], name, msg.raw['Type'], path)

                   #判断调戏功能是否打开
                   if int(g['is_flirt']) == 1:
                       if "@小助手" in msg.text:
                           conte = msg.text.replace('@小助手', '')
                           ret = self.auto_ai(conte)

                           try:
                               zhushou = self.bot.self          #获取机器人本身
                               path2 = "./static/小助手.jpg"
                               zhushou.get_avatar(path2)
                           except:
                               path2 = ''

                           # 插入数据库
                           self.insert_message(msg.raw['CreateTime'], "小助手", ret, g['ba_id'], name, msg.raw['Type'], path2.lstrip('.'))

                           return ret



    # 插入数据库
    def insert_message(self, sendTime, nikename, content, ba_id, name, type , head_img):
       timeArray = time.localtime(sendTime)

       sendTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
       params = parse.urlencode({'nickname': nikename, 'content': content, 'send_time': sendTime,'wechat': nikename, 'ba_id': ba_id, 'group_name': name, 'type': type, 'head_img': head_img})
       #print(params)
       request.urlopen(url+"/bot/collect_message.php?%s" % params)

    #尬聊
    def sel_this_day_info(self):
        @self.bot.register(Friend, msg_types=TEXT)
        def sel_friend(msg):
            if (msg.type == 'Text'):
                ret = self.auto_ai(msg.text)
            else:
                ret = '[奸笑][奸笑]'

            print('[发送]' + str(ret))
            return ret

    #图灵机器人
    def auto_ai(self, text):
        url = "http://www.tuling123.com/openapi/api"
        api_key = "fde3ce19748b4768ae4dc9c5273c4478"
        payload = {
            "key": api_key,
            "info": text,
            "userid": "316890"
        }
        r = requests.post(url, data=json.dumps(payload))
        result = json.loads(r.content.decode())
        if ('url' in result.keys()):
            return result["text"] + result["url"]
        else:
            return result["text"]

    #上传到阿里云
    def oss_upload(self, img_key, img_path):
        accessKeyId = 'LTAIuTfkvjnNg54j'
        accessKeySecret = 'OTETap8a971xgfYdNCawWuHTkbR5dj'
        bucket_name = 'ccvthb'
        aliyun_url = 'oss-cn-beijing.aliyuncs.com'
        auth = oss2.Auth(accessKeyId, accessKeySecret)
        bucket = oss2.Bucket(auth, aliyun_url, bucket_name)
        bucket.put_object_from_file(img_key, img_path)
        url = "http://" + bucket_name+"."+aliyun_url+"/"+img_key
        return url


