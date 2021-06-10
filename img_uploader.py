import time
import requests
import logging
import traceback
import json

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
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "referer": "https://greatposterwall.com/upload.php?action=image",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    }
    def __init__(self, cookies):
        self.upload_url = "https://up-as0.qiniup.com"
        self.img_host_url = "https://img.kshare.club/"
        self.timer = Timer(1, 2)
        self.token_timer = Timer(5, 10)
        self.cookies = cookies

        self.token = self.get_token()

    def _upload(self, img_path):
        self.timer.wait()
        files = {
            "file": ("1.png", open(img_path, "rb"), "image/png"),
            "token": (None, self.token)
        }
        r = requests.post(self.upload_url, files=files)
        return json.loads(r.text)

    def upload(self, img_path):
        resp = self._upload(img_path)
        if "error" in resp.keys():
            if resp["error"] == "expired token":
                self.token = self.get_token()
                resp = self._upload(img_path)
        uploaded_url = "{}{}".format(self.img_host_url, resp["key"])
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
