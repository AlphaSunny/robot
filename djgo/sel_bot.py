from wxpy import *
import json
import requests
import datetime
import time
import hashlib
import random
import threading


def send_message():
    bot = Bot(cache_path=True, qr_callback=get_qr)
    record_group = ensure_one(bot.groups().search('测试'))
    record_group.send("222222222")
    exit()
    status = 0

    def main():
        now = datetime.datetime.now()
        # 获取本地json
        rows = get_json()
        for i in rows:
            h = int(i['time'].split(":")[0])
            m = int(i['time'].split(":")[1])
            s = int(i['time'].split(":")[-1])
            # print(h, m, s)
            if now.hour == h and now.minute == m and now.second == s:
                record_group.send(i['content'])
                break

        time.sleep(1)
        main()

    if status != 1:
        main()
        status = 1

t = threading.Thread(target=send_message, name='send_message')
t.start()



# def send_message():
#     bot = Bot(cache_path=True, qr_callback=get_qr)
#     record_group = ensure_one(bot.groups().search('测试'))
#
#
#     status = 0
#     def main():
#         now = datetime.datetime.now()
#         #获取本地json
#         rows = get_json()
#         for i in rows:
#             h = int(i['time'].split(":")[0])
#             m = int(i['time'].split(":")[1])
#             s = int(i['time'].split(":")[-1])
#             # print(h, m, s)
#             if now.hour == h and now.minute == m and now.second == s:
#                 record_group.send(i['content'])
#                 break
#
#         time.sleep(1)
#         main()
#
#     if status != 1:
#         main()
#         status = 1

    # @bot.register(record_group)
    # def group_message(msg):
    #     print('[接收]' + str(msg.text))
    #     if (msg.type != 'Text'):
    #         ret = '[奸笑][奸笑]'
    #     else:
    #         ret = auto_ai(msg.text)
    #
    #     print('[发送]' + str(ret))
    #     return ret



    # embed()



#生成本地json文件
def set_json():
    url = 'http://phpmanong.cn/api/bot/timer.php'
    req = requests.get(url)
    dict = json.loads(req.text)['rows']
    # dumps 将数据转换成字符串
    json_str = json.dumps(dict)

    # loads: 将 字符串 转换为 字典
    new_dict = json.loads(json_str)
    # print(new_dict)

    with open("timer.json", "w") as f:
        json.dump(new_dict, f)
    #每30秒调一次接口
    time.sleep(30)
    set_json()

#获取本地json文件内容
def get_json():
    with open("timer.json", 'r') as load_f:
        load_dict = json.load(load_f)
        return load_dict



def get_qr(uuid,status,qrcode):
    address = "./static/abc.png"
    with open(address, "wb") as f:
        f.write(qrcode)

def auto_ai(text):
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

def get_guid():
    seed = "1234567890abcdefghijklmnopqrstuvwxyz"
    sa = []
    for i in range(12):
        sa.append(random.choice(seed))
    salt = ''.join(sa)

    hash = hashlib.md5()
    hash.update(salt.encode())
    md5ha = hash.hexdigest()
    return  md5ha


