import time
import requests
import logging
import traceback
import json
import brotli

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class Timer(object):

    def __init__(self, count, interval):
        self.history = [0 for _ in range(count)]
        self.interval = interval

    def wait(self):
        t = time.time()
        if t - self.history[0] < self.interval:
            time.sleep(self.interval - (t - self.history[0]) + 0.1)
            t = time.time()
        self.history = self.history[1:] + [t,]

class ImgUploader(object):
    HEADERS = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "referer": "https://greatposterwall.com/upload.php?action=image",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    }
    def __init__(self, cookies):
        #self.upload_url = "https://up-as0.qiniup.com"
        self.upload_url = "https://greatposterwall.com/upload.php?action=imgupload"
        self.img_host_url = "https://img.kshare.club/"
        self.timer = Timer(1, 2)
        self.token_timer = Timer(5, 10)
        self.cookies = cookies
        #self.token = self.get_token()

    def _upload(self, img_path):
        self.timer.wait()
        files = {'images[]': open(img_path, "rb")}

        r = requests.post(self.upload_url, headers=ImgUploader.HEADERS, cookies=self.cookies, files=files)
        return json.loads(r.text)

    def upload(self, img_path):
        resp = self._upload(img_path)
        if "error" in resp.keys():
            print(resp["error"])
        uploaded_url = "{}".format(resp["files"][0]["name"])
        logging.info("uploaded to: {}".format(uploaded_url))
        return uploaded_url

    def get_token(self):
        self.token_timer.wait()
        r = requests.get("https://greatposterwall.com/upload.php?action=image", 
                         headers=ImgUploader.HEADERS, cookies=self.cookies)
        startstr = "ImgUpload('"
        endstr = "'"
        left = r.text.find(startstr)
        right = r.text.find(endstr, left+len(startstr))
        token = r.text[left+len(startstr):right]
        logging.info("new token: {}".format(token))
        return token
