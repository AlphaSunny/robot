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
import djgo.common as a
import base64



url = a.url()

class Robot(object):
    def __init__(self, bot):
        self.bot = bot
        self.t1 = ''
        self.t2 = ''
        self.t3 = ''
        self.t4 = ''
        self.t5 = ''
        self.t6 = ''
        self.t7 = ''
    #聊天
    def send_to_message(self):

        # fi = self.bot.friends().search('Gavin')[0]
        # print(fi)
        # fi.set_remark_name("宋")
        #
        # fri = self.bot.friends()
        # for frinend in fri:
        #     print(frinend)



        data = request.urlopen(url + "/bot/get_qrcode.php").read()
        data_json = json.loads(data.decode("utf-8"))
        dict = data_json['rows']
        if int(dict['robot_alive']) != 1:

            # 生成本地group json文件，因为下面的进程会卡死，所以先生成一次
            self.set_group_json_first()

            # 添加好友
            self.add_friends()

            #个人图灵机器人
            self.sel_frind_message()

            #群聊图灵机器人
            #self.start_record_bot()

            # 收集群聊信息
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    self.start_record_bot(name['name'])


            #循环调用接口生成json,循环调用json判断时间
            #注：不能写t1 = threading.Thread(target=self.set_timer())
            threads = []
            self.t1 = threading.Thread(target=self.set_timer)
            threads.append(self.t1)
            self.t2 = threading.Thread(target=self.timer_run)
            threads.append(self.t2)
            self.t3 = threading.Thread(target=self.judge_group_or_same)
            threads.append(self.t3)
            self.t4 = threading.Thread(target=self.check_login)
            threads.append(self.t4)
            self.t5 = threading.Thread(target=self.send_money_to_ccvt)
            threads.append(self.t5)
            self.t6 = threading.Thread(target=self.storage_members)
            threads.append(self.t6)
            self.t7 = threading.Thread(target=self.check_chat)
            threads.append(self.t7)
            for t in threads:
                t.start()
            for t in threads:
                t.join()

    # 每分钟判断一次**分钟内是否有人聊天，如果没人聊天，推送文章
    def check_chat(self):
        while True:
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    if name['name'] == "WindWin Tec Family":
                        now = datetime.datetime.now()
                        if ((now.hour >= 8 and now.minute >= 20) and now.hour < 10) or ((now.hour >= 12 and now.minute >= 20) and now.hour < 14) or ((now.hour >= 20 and now.minute >= 20) and now.hour < 22):

                            params = parse.urlencode({'group_name': name['name']})
                            data = request.urlopen(url + "/bot/check_chat.php?%s" % params).read()
                            data_json = json.loads(data.decode("utf-8"))
                            if data_json['is_hive'] == 2:
                                result = request.urlopen(url + "/bot/get_news.php").read()
                                result_text = json.loads(result.decode("utf-8"))

                                g = self.bot.groups().search(name['name'])[0]
                                g.send(result_text['content'])

            time.sleep(1200)


    #存储群成员(5分钟更新一次)
    def storage_members(self):
        while True:
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    #先删除
                    params = parse.urlencode({'group_id': name['id']})
                    request.urlopen(url + "/bot/del_storage_members.php?%s" % params)

                    group = self.bot.groups().search(name['name'])[0]
                    group.update_group
                    for g in group.members:
                        #存储
                        params = parse.urlencode(
                            {'name': g.name, 'group_name': name['name'], 'group_id': name['id']})
                        urls = url + "/bot/storage_members.php?%s" % params
                        request.urlopen(urls)

            time.sleep(300)






    #登录状态判断
    def check_login(self):
        while True:
            if self.bot.alive == True:
                status = 1
            else:
                status = 2

            params = parse.urlencode({'robot_alive': status})
            request.urlopen(url + "/bot/bot_alive.php?%s" % params)

            #判断微信退出，线程退出,发送验证码通知
            if status == 2:
                request.urlopen(url + "/bot/send_message.php").read()

                self.t1.stop()
                self.t2.stop()
                self.t3.stop()
                self.t4.stop()
                self.t5.stop()
                self.t6.stop()
                self.t7.stop()


            time.sleep(60)



    # 每天凌晨一点执行送币（昨天的）
    def send_money_to_ccvt(self):
        while True:
            now = datetime.datetime.now()
            if now.hour == 22 and now.minute == 10:
                request.urlopen(url + "/crontab/send_money_ccvt.php").read()
            # 每隔60秒检测一次
            time.sleep(60)



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

            #所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            for a in dict2:
                if (a['id'] not in id) or (a['name'] not in name) or (a['ba_id'] not in ba_id):
                    if a['name'] in all:
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

            # 所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            group_list = self.get_group_json()
            if week not in da:

                if date_of not in da:

                    for name in group_list:

                        if name['name'] in all:

                            group = self.bot.groups().search(name['name'])[0]
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
                                    elif now.hour == 8:
                                        params = parse.urlencode({'group_name': name['name']})
                                        data = request.urlopen(url + "/bot/search_statistical.php?%s" % params).read()
                                        data_json = json.loads(data.decode("utf-8"))
                                        content = i['content'] + "，昨日ccvt奖励记录查看地址:" + data_json['url']
                                    else:
                                        content = i['content']

                                    group.send(content)
                                    break
            else:
                for name in group_list:

                    if name['name'] in all:
                        group = self.bot.groups().search(name['name'])[0]
                        now = datetime.datetime.now()
                        rows = self.get_timer()
                        for i in rows:
                            h = int(i['time'].split(":")[0])
                            m = int(i['time'].split(":")[1])

                            if now.hour == h and now.minute == m and name['id'] == i['group_id'] and int(name['is_del']) == 1:
                                if now.hour == 22:
                                    params = parse.urlencode({'group_name': name['name']})
                                    data = request.urlopen(url + "/bot/search_chat.php?%s" % params).read()
                                    data_json = json.loads(data.decode("utf-8"))
                                    content = i['content'] + "，今日聊天记录查看地址:" + data_json['url']
                                    group.send(content)
                                    break
                                elif now.hour == 12:
                                    params = parse.urlencode({'group_name': name['name']})
                                    data = request.urlopen(url + "/bot/search_statistical.php?%s" % params).read()
                                    data_json = json.loads(data.decode("utf-8"))
                                    content = "大家周末好，早上睡懒觉迟到了😝，不好意思" + "，昨日ccvt奖励记录查看地址:" + data_json['url']
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

           # self.bot.enable_puid('wxpy_puid.pkl')
           # print(msg)
           # f = self.bot.friends().search(msg.raw['ActualNickName'])[0]
           # print(f)
           # print(f.puid)
           # print(msg.raw)


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
                       if "@风赢小助手" in msg.text:
                           conte = msg.text.replace('@风赢小助手', '')
                           ret = self.auto_ai(conte)

                           try:
                               zhushou = self.bot.self          #获取机器人本身
                               path2 = "./static/风赢小助手.jpg"
                               zhushou.get_avatar(path2)
                           except:
                               path2 = ''

                           # 插入数据库
                           self.insert_message(msg.raw['CreateTime'], "风赢小助手", ret, g['ba_id'], name, msg.raw['Type'], path2.lstrip('.'))

                           return ret



    # 插入数据库
    def insert_message(self, sendTime, nikename, content, ba_id, name, type , head_img):
       timeArray = time.localtime(sendTime)

       sendTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
       params = parse.urlencode({'nickname': nikename, 'content': content, 'send_time': sendTime,'wechat': nikename, 'ba_id': ba_id, 'group_name': name, 'type': type, 'head_img': head_img})
       #print(params)
       request.urlopen(url+"/bot/collect_message.php?%s" % params)

    #好友聊天信息
    def sel_frind_message(self):
        @self.bot.register(Friend, msg_types=TEXT)
        def sel_friend(msg):
            # print(msg.sender.name)
            # print(msg.sender.remark_name)

            if (msg.raw['Type'] == 'Text'):
                ret = self.auto_ai(msg.text)
            else:
                ret = '[奸笑][奸笑]'

            try:
                my_friend = self.bot.friends().search(msg.sender.name)[0]
                path = "./static/" + msg.sender.name + ".jpg"
                my_friend.get_avatar(path)

                # 上传到阿里云
                path = self.oss_upload('img/' + msg.sender.name + ".jpg", path)

                # 删除本地图片
                os.remove(path)
            except:
                path = ''


            if msg.raw['Type'] == "Picture" or msg.raw['Type'] == "Video" or msg.raw['Type'] == "Recording":
                t = "./static/" + msg.raw['FileName']
                msg.get_file(t)  # 下载图片，视频

                # 上传到阿里云
                content = self.oss_upload('img/' + msg.raw['FileName'], t)

                # 删除本地文件
                os.remove(t)
            else:
                content = msg.text
            # 插入数据库
            self.insert_message(msg.raw['CreateTime'], msg.sender.name, content, 'friend', 'friend', msg.raw['Type'], path)

            # 插入数据库
            self.insert_message(msg.raw['CreateTime'], "小助手", ret, 'friend', 'friend', msg.raw['Type'], '')

           #print('[发送]' + str(ret))
            return ret

    # 好友请求
    def add_friends(self):
        @self.bot.register(msg_types="Friends")
        def auto_accept_friends(msg):
            new_friend = msg.card.accept()
            self.bot.enable_puid('wxpy_puid.pkl')
            frind_puid = new_friend.puid
            #new_friend.set_remark_name(new_friend.remark_name + "-" + frind_puid)
            new_friend.set_remark_name(new_friend.remark_name)
            #new_friend.send("你好，我是您的CCVT小助手，欢迎加入，您的CCVT账户代码是" + str(frind_puid))
            new_friend.send("你好，我是您的CCVT小助手，欢迎加入")

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


