# gpw mkv uploady
为mkv文件生成GreatPosterWall站点上传所需的信息

## 功能
批量扫描电影文件夹内的mkv

* 截图
* 将截图上传gpw图床
* 生成mediainfo
* 重新制种
重新制种会仅保留主mkv文件忽略掉sample以及其他无关文件

扫描支持：
* 单文件mkv
* 子文件夹下的mkv，同一个子文件夹下只会保留一个
扫描会自动过滤被禁止的发布组的内容

不支持：
* 子文件夹下有多个mkv，比如合集/剧集

## 安装依赖

* 安装python3并安装requests
```
sudo pip3 install requests
```
* mediainfo和ffmpeg，例子：对于ubuntu
```
sudo apt-get install mediainfo ffmpeg
```

## 运行
首先复制一份配置文件：
```
cp config.py.example config.py
```
然后按照其中提示编辑`config.py`

之后直接运行
```
python3 run_all.py
```