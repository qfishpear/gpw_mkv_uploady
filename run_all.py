import logging
import json
import os
import upload_task
import img_uploader
from config import CONFIG

def is_valid_mkvname(mkvpath):
    BANNED_KEYWORDS = [
        # 忽略剧集
        "S0", "E0",
        # 忽略sample
        "sample", 
        # 忽略被禁止的发布组
       "aXXo", "BRrip", "CM8", "CrEwSaDe", "DNL", "EVO", "FaNGDiNG0", "FRDS",
       "HD2DVD", "HDTime", "iPlanet", "KiNGDOM", "Leffe", "mHD", "mSD", "nHD", 
       "nikt0", "nSD", "NhaNc3", "PRODJi", "RDN", "SANTi", "STUTTERSHIT", "TERMiNAL", 
       "ViSION", "WAF", "x0r", "YIFY"
    ]
    for groupname in BANNED_KEYWORDS:
        if groupname.lower() in mkvpath.lower():
            return False
    return True

def gen_tasks(film_root, uploady_root):
    tasks = []
    for item in os.listdir(film_root):
        p = os.path.join(film_root, item)
        if os.path.isfile(p):
            if os.path.splitext(p)[1] == ".mkv" and is_valid_mkvname(p):
                resultdir = os.path.join(uploady_root, os.path.splitext(os.path.split(p)[1])[0])
                tasks.append({"mkvpath": p, "resultdir":resultdir, "is_single_file":True})
        if os.path.isdir(p):
            for inneritem in os.listdir(p):
                p2 = os.path.join(p, inneritem)
                if os.path.splitext(p2)[1] == ".mkv" and is_valid_mkvname(p2):
                    resultdir = os.path.join(uploady_root, os.path.splitext(os.path.split(p2)[1])[0])
                    tasks.append({"mkvpath": p2, "resultdir":resultdir, "is_single_file":False})
                    break
    return tasks

tasks = gen_tasks(film_root=CONFIG["source_dir"], uploady_root=CONFIG["uploady_dir"])
logging.info("{} films generated".format(len(tasks)))
SCREENSHOT = CONFIG["pipeline"]["screenshot"]
if SCREENSHOT["screenshot"] and SCREENSHOT["upload_to_image_host"]:
    imguploader = img_uploader.ImgUploader(cookies=CONFIG["gpw"]["cookies"])
else:
    imguploader = None
for i, t in enumerate(tasks):
    logging.info("{}/{}: {}".format(i+1, len(tasks),  t["mkvpath"]))
    task = upload_task.UploadTask(
        pipeline=CONFIG["pipeline"],
        mkvpath=t["mkvpath"],
        resultdir=t["resultdir"],
        is_single_file=t["is_single_file"],
        imguploader=imguploader,
    )
    task.run_all()