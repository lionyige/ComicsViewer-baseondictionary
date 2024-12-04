# -*- coding: utf-8 -*-
# python 3.7.0

import os
import time
import shelve
import sys

ORIGINAL_BASE_PATH = os.getcwd()
BASE_PATH =sys.argv[1]

INDEX_HTML = "/index.html"
CONTENT_HTML = "/"+sys.argv[1].split('\\')[-1]+".html"

TEMPLETE_URL =os.path.dirname(os.path.abspath(__file__))
TEMPLETE_HTML=os.path.dirname(os.path.abspath(__file__))+"/h/templete.html"
INDEX_TEMPLETE_HTML = os.path.dirname(os.path.abspath(__file__))+"/h/index_templete.html"

IMG_SUFFIX = [".jpg", ".png", ".jpeg", ".gif",".webp"]

BASE_DIR=sys.argv[1]
DATA_PATH_UP=BASE_DIR+"/data"
DATA_PATH = DATA_PATH_UP+"/data"
PARENT_DIRS_WITH_IMAGES=set()
def createComicItems(title, content_path, first_img, count):
	templete = r'<li><a href="{url}" target="_blank" title="{title}"><h2>{title}</h2><div class="image"><img class="lazy" src="{first_img}"><table class="data"><tr><th scope="row">枚数</th><td>{count}枚</td></tr><tr><td class="tag" colspan="2"><span>{title}</span></td></tr></table></div><p class="date">{date}</p></a></li><!--{comic_contents}-->'
	templete = templete.replace(r"{url}", content_path + CONTENT_HTML)
	templete = templete.replace(r"{title}", title)
	templete = templete.replace(r"{count}", str(count))
	templete = templete.replace(r"{first_img}", content_path+"/"+first_img)
	date = time.localtime(os.stat(content_path).st_ctime)
	templete = templete.replace(r"{date}", ("%d-%d-%d" % (date.tm_year,date.tm_mon,date.tm_mday)))
	return templete

def getTempleteHtml(templeteURL):
	templete = open(templeteURL, "r", encoding="UTF-8")
	htmlStr = templete.read()
	templete.close()
	return htmlStr

def output2Html(htmlContent, file):
	output = open(file, "w", encoding="UTF-8")
	output.write(htmlContent)
	output.flush()
	output.close()

def createOptions(imgData):
	options = ""
	_i = 0
	for _img in imgData:
		options += ('<option value="%d" file="%s">第%d页</option>' % (_i, _img, _i+1))
		_i += 1
	return options

def createImgList(content_path):
	imgs = []
	for _dir in os.listdir(content_path):
		if os.path.splitext(_dir)[1].lower() in IMG_SUFFIX:
			imgs.append(_dir)
	try:
		imgs.sort(key=lambda x:int(x[:-4]))
	except:
		pass
	return imgs

def createContentHtml(contentPath):
	imgData = createImgList(contentPath)
	if len(imgData) == 0 or imgData == None:	return
	count = len(imgData)
	options = createOptions(imgData)
	htmlStr = getTempleteHtml(TEMPLETE_HTML)
	title = contentPath.split('\\')[-1]
	htmlStr = htmlStr.replace(r"{imgData}", "var imgData="+str(imgData))
	htmlStr = htmlStr.replace(r"{template_url}", TEMPLETE_URL)
	htmlStr = htmlStr.replace(r"{title}", title).replace(r"{options}", options)
	htmlStr = htmlStr.replace(r"{count}", str(count)).replace(r"{first_img}", imgData[0])
	try:
		htmlStr = htmlStr.replace(r"{next_img}", imgData[1])
	except IndexError:
		htmlStr = htmlStr.replace(r"{next_img}", imgData[0])
	output2Html(htmlStr, contentPath + CONTENT_HTML)
	return [title, contentPath, imgData[0], count]

def createDataDictionaryifNotExite(folder_path):
	if not os.path.exists(folder_path):
		# 创建文件夹
		os.makedirs(folder_path)

def pushData(data):
	createDataDictionaryifNotExite(DATA_PATH_UP)
	with shelve.open(DATA_PATH) as write:
		write[data[0]] = data

def checkData():
	with shelve.open(DATA_PATH) as read:
		keys = list(read.keys())
		for key in keys:
			if not checkFileExist(read[key][1]+CONTENT_HTML):
				print("移除： ", read[key])
				del(read[key])

def getData():
	data = []
	with shelve.open(DATA_PATH) as read:
		keys = list(read.keys())
		for key in keys:
			data.append(read[key])
	return data

def createIndexHtml():
	checkData()
	datas = getData()
	indexStr = getTempleteHtml(INDEX_TEMPLETE_HTML)
	indexStr = indexStr.replace(r"{template_url}", TEMPLETE_URL)
	for data in datas:
		_s = createComicItems(data[0], data[1], data[2], data[3])
		indexStr = indexStr.replace(r"<!--{comic_contents}-->", _s)
	output2Html(indexStr, BASE_PATH + INDEX_HTML)


def checkFileExist(fileURI):
	if os.path.isfile(fileURI):
		return True
	return False

def getContentPaths(path):
	contentPaths = []	
	for _path in os.listdir(path):
		_dir = path + "/" + _path
		if os.path.isdir(_dir):
			contentPaths.append(_dir)
	return contentPaths

def traversedirsoath(base_dir):
	image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff','.webp',)
	for root, dirnames, filenames in os.walk(base_dir):
		# 检查当前目录中的文件
		if any(f.lower().endswith(image_extensions) for f in filenames):
			PARENT_DIRS_WITH_IMAGES.add(root)
	# 输出包含图片的上一级目录
	# for parent_dir in PARENT_DIRS_WITH_IMAGES:
	# 	print(parent_dir)


# def get_substring_before_last_backslash(path):
# 	# 使用 rfind 找到最后一个 \ 的索引
# 	# 使用 rsplit 从字符串右侧分割，最多分割成 2 部分
# 	parts = path.rsplit('\\', 2)
#
# 	# 如果分割得到的部分数量少于 2，说明没有足够的反斜杠
# 	# 否则返回倒数第二个部分
# 	return parts[0] if len(parts) > 1 else ''


if __name__ == '__main__':
	traversedirsoath(BASE_DIR)
	for contentPath in PARENT_DIRS_WITH_IMAGES:
		if checkFileExist(contentPath + CONTENT_HTML):	continue
		data = createContentHtml(contentPath)
		if data is not None:
			print("新增： ", data)
			pushData(data)
	createIndexHtml()