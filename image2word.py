import base64
import csv
import hashlib
import json
import time
from pathlib import Path

import requests

IMAGE_DIR = 'E:/PythonProjects/video/'
# 印刷文字识别 webapi 接口地址
URL = 'http://webapi.xfyun.cn/v1/service/v1/ocr/general'
APPID = '5d3d42cf'
API_KEY = '09dabaec5e1d61fddcba4abc49d619bf'


def getHeader():
    #  当前时间戳
    curTime = str(int(time.time()))
    #  支持语言类型和是否开启位置定位(默认否)
    param = {"language": "cn|en", "location": "false"}
    param = json.dumps(param)
    paramBase64 = base64.b64encode(param.encode('utf-8'))

    m2 = hashlib.md5()
    str1 = API_KEY + curTime + str(paramBase64, 'utf-8')
    m2.update(str1.encode('utf-8'))
    checkSum = m2.hexdigest()
    # 组装http请求头
    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    return header


for image_dir in Path(IMAGE_DIR).iterdir():
    if image_dir.is_dir():
        result = dict()
        images = image_dir.glob('*.jpg')
        for image in images:
            # 上传文件并进行base64位编码
            with open(str(image), 'rb') as file:
                file = file.read()
            file_base64 = str(base64.b64encode(file), 'utf-8')
            data = {'image': file_base64}
            r = requests.post(URL, data=data, headers=getHeader())
            json_data = json.loads(r.text)
            result[image.name] = ''
            for block in json_data['data']['block']:
                for line in block['line']:
                    for word in line['word']:
                        result[image.name] += ' ' + word['content']
        with open(str(image_dir) + '.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            for str_time, value in result.items():
                writer.writerow([str_time, value])
