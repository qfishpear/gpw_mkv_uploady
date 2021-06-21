import os
import logging
import subprocess
import time
import shutil
import requests
import json
import traceback
from img_uploader import ImgUploader
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class UploadTask(object):

    def __init__(self, *, 
        pipeline: dict,
        mkvpath: str,
        resultdir: str,
        is_single_file: bool,
        imguploader=None,
        ptpimguploader=None,
    ):
        """
        pipeline: all operations to be done, see config.py for details
        mkvpath: path to .mkv file
        resultdir: path to save the uploady information
        is_single_file: whether the .mkv file is only a single file or under a folder
        """
        self.pipeline = pipeline
        self.mkvpath = mkvpath
        self.resultdir = resultdir        
        self.is_single_file = is_single_file
        self.imguploader = imguploader
        self.ptpimguploader = ptpimguploader

    def run_all(self):
        filename = os.path.split(self.mkvpath)[1]
        logging.info("running task for {} result will be saved to {}".format(filename, self.resultdir))
        if not os.path.exists(self.resultdir):
            os.makedirs(self.resultdir)
        if self.pipeline["screenshot"]["screenshot"]:
            SCREENSHOT= self.pipeline["screenshot"]
            logging.info("generating screenshot")
            screenshot_paths = self.gen_screenshot(quantiles=SCREENSHOT["quantiles"])
            if SCREENSHOT["upload_to_image_host"]:
                self.upload_to_image_host(screenshot_paths)
            if SCREENSHOT["upload_to_ptpimg"]:
                self.upload_to_ptpimg(screenshot_paths)
        if self.pipeline["mediainfo"]:
            logging.info("generating mediainfo")
            self.gen_mediainfo()
        if self.pipeline["mktorrent"]:
            logging.info("generating torrent")
            self.gen_torrent()
        if self.pipeline["mkv_softlink"]:
            logging.info("generating mkv softlink")
            self.gen_mkv_softlink()

    def gen_screenshot(self, quantiles):
        length_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", self.mkvpath]
        length = float(subprocess.run(length_cmd, check=True, capture_output=True).stdout)    
        timestamps = [int(length * quantile) for quantile in quantiles]
        logging.info("video length: {}".format(time.strftime('%H:%M:%S', time.gmtime(length))))
        screenshot_paths = []
        for t in timestamps:
            target = os.path.join(self.resultdir, "{}.png".format(time.strftime('%H_%M_%S', time.gmtime(t))))
            screenshot_paths.append(target)
            if not os.path.exists(target):
                screenshot_cmd = ["ffmpeg", "-ss", str(t), "-y", "-i", self.mkvpath, "-vframes", "1", "-vcodec", "png", target]
                subprocess.run(screenshot_cmd, check=True, capture_output=True)
        return screenshot_paths

    def upload_to_image_host(self, screenshot_paths):
        """
        上传至gpw官方图床
        """
        uploaded_result = os.path.join(self.resultdir, "screenshot_bbcode.txt")
        if not os.path.exists(uploaded_result):
            uploaded_urls = []
            for img_path in screenshot_paths:
                logging.info("uploading {}".format(img_path))
                uploaded_urls.append(self.imguploader.upload(img_path))
            with open(uploaded_result, "w") as f:
                for url in uploaded_urls:
                    f.write("[img]{}[/img]\n".format(url))

    def upload_to_ptpimg(self, screenshot_paths):
        uploaded_result = os.path.join(self.resultdir, "screenshot_bbcode_ptpimg.txt")
        if not os.path.exists(uploaded_result):
            uploaded_urls = []
            for img_path in screenshot_paths:
                logging.info("uploading {} to ptpimg".format(img_path))
                uploaded_urls.append(self.ptpimguploader.upload_file(img_path)[0])
            with open(uploaded_result, "w") as f:
                for url in uploaded_urls:
                    f.write("[img]{}[/img]\n".format(url))

    def gen_mediainfo(self):
        with open(os.path.join(self.resultdir, "mediainfo.txt"), "w") as f:
            subprocess.run(["mediainfo", self.mkvpath], check=True, stdout=f)

    def gen_mkv_softlink(self):
        filename = os.path.split(self.mkvpath)[1]
        if not os.path.exists(os.path.join(self.resultdir, filename)):
            symlink_cmd = ["ln", "-s", self.mkvpath, self.resultdir]
            subprocess.run(symlink_cmd, check=True)

    def gen_torrent(self):
        if self.is_single_file:
            torrent_content = self.mkvpath
        else:
            filename = os.path.split(self.mkvpath)[1]
            pathname = os.path.split(os.path.split(self.mkvpath)[0])[1]
            tmpdir = os.path.join(self.resultdir, pathname)
            if not os.path.exists(tmpdir):
                os.makedirs(tmpdir)
            if not os.path.exists(os.path.join(tmpdir, filename)):
                hardlink_cmd = ["ln", "-s", self.mkvpath, tmpdir]
                subprocess.run(hardlink_cmd, check=True)
            torrent_content = tmpdir
        torrentname = "{}.torrent".format(os.path.splitext(os.path.split(self.mkvpath)[1])[0])
        torrentpath = os.path.join(self.resultdir, torrentname)
        if os.path.exists(torrentpath) and os.path.getsize(torrentpath) == 0:
            os.remove(torrentpath)
        if not os.path.exists(torrentpath):
            mktorrent_cmd = ["mktorrent", "-o", torrentpath, torrent_content]
            subprocess.run(mktorrent_cmd, check=True)
        if not self.is_single_file:
            shutil.rmtree(torrent_content)