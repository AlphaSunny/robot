from djgo.oss_upload import Oss_up

#上传到阿里云
path = Oss_up.upload("img/abc.png", "../static/abc.png")

print(path)