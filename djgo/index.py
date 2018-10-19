from django.shortcuts import render_to_response
# import djgo.sel_bot
from djgo.robot import Robot
from wxpy import *



def index(request):
    return render_to_response('index.html')

def show_uuid(uuid, status, qrcode):
    address = "./static/abc.png"
    with open(address, "wb") as f:
        f.write(qrcode)

    # if int(status)==0:
    #     return render_to_response('index.html')
    #s
    # return render_to_response('index.html')


def search(request):
    bot = Bot(console_qr=True, cache_path=True, qr_callback=show_uuid)

    rot = Robot(bot)
    rot.send_to_message()

    embed()
    return render_to_response('index.html')





def set_json(request):
    # djgo.sel_bot.set_json()
    print(222)




