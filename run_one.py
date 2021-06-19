import logging
import json
import os
import upload_task
import img_uploader
import argparse
from config import CONFIG

parser = argparse.ArgumentParser()
parser.add_argument("--mkvpath", required=True, help=".mkv文件的路径 path to the .mkv file")
parser.add_argument("--resultdir", required=True, help="存储结果的文件夹路径 path to the result dir")
parser.add_argument("--is_single_file", default=False, action="store_true", help="如果是单文件mkv而不是文件夹下的mkv，请使用此选项 add this flag if it's a single .mkv file instead of a .mkv file under certain folder")
args = parser.parse_args()

SCREENSHOT = CONFIG["pipeline"]["screenshot"]
if SCREENSHOT["screenshot"] and SCREENSHOT["upload_to_image_host"]:
    imguploader = img_uploader.ImgUploader(cookies=CONFIG["gpw"]["cookies"])
else:
    imguploader = None
task = upload_task.UploadTask(
    pipeline=CONFIG["pipeline"],
    mkvpath=args.mkvpath,
    resultdir=args.resultdir,
    is_single_file=args.is_single_file,
    imguploader=imguploader,
)
task.run_all()