# gpw mkv uploady
为mkv文件生成GreatPosterWall站点上传所需的信息

## 功能
批量扫描电影文件夹内的mkv, 会自动过滤剧集和被禁止的发布组的内容

* 截图
* 将截图上传gpw图床或ptpimg
* 生成mediainfo
* 重新制种
重新制种会仅保留主mkv文件忽略掉sample以及其他无关文件

扫描支持：
* 单文件mkv
* 子文件夹下的mkv，同一个子文件夹下只会保留一个

## 安装依赖

* 安装python3并安装requests
```
sudo pip3 install requests ptpimg_uploader
```
* mediainfo、ffmpeg和mktorrent，例子：对于ubuntu
```
sudo apt-get install mediainfo ffmpeg mktorrent
```

## 运行
首先复制一份配置文件：
```
cp config.py.example config.py
```
然后按照其中提示编辑`config.py`

之后直接运行对整个`CONFIG["source_dir"]`下的mkv文件生成上传信息
```
python3 run_all.py
```

或者运行
```
python3 run_one.py --mkvpath mkv文件的路径 --resultdir 生成的结果文件夹的目录 [--is_single_file]
```
