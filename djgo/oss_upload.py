# -*- coding: utf-8 -*-
import oss2

# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
accessKeyId = 'LTAIuTfkvjnNg54j'
accessKeySecret = 'OTETap8a971xgfYdNCawWuHTkbR5dj'
bucket_name = 'ccvthb'
aliyun_url = 'oss-cn-beijing.aliyuncs.com'


class Oss_up:

    def upload(self, path, img_path):
        auth = oss2.Auth(accessKeyId, accessKeySecret)
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(auth, aliyun_url, bucket_name)
        bucket.put_object_from_file(path, img_path)

        url = "http://"+bucket_name + "." + aliyun_url + "/" + path

        print(url)

        return url

