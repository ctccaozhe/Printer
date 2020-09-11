#coding=utf-8

#调用usb热敏打印机
#通过rawprint.exe发送打印数据给打印机
#可以发送控制命令与普通文本

import time
import random
import os
import uuid

#esc指令
escConst ={'esc':27,'gs':29,'lf':10,'dle':16,'eot':4,'enq':5,'dc4':20,'=':61}

#当前工作目录
workingDir = os.path.dirname(os.path.abspath(__file__))

#将ESC指令转为整数
def escToken2Int(token):
	token = token.lower()
	if escConst.has_key(token):
		return escConst[token]
	if token.isdigit():
		return int(token)
	return ord(token)

#将ESC指令串转为列表
def escStr2List(escStr):
	tmpList = escStr.split(' ')
	return map(escToken2Int,tmpList)

#将ESC指令串转为可发送给打印机的数据
def escStr2RawData(escStr):
	return list2RawData(escStr2List(escStr))

#列表转为可发送给打印机的数据
def list2RawData(intList):
	template = "%s"*len(intList)
	return template%tuple(map(chr,intList))

#发送打印数据的可执行文件名
exeFile = workingDir +'\\exe\\RawPrint.exe'

#模板文件名保留，为以后打印复杂内容做准备
#templateFile = workingDir +'\\template\\temp1.txt'


#打印助手类
class PrintHelper:

	def __init__(self,printerName):
		self.printerName = printerName
		self.reset()

	#重置，清空缓冲区
	def reset(self):
		self.buffer =''
		self.appendCmd("esc @")

	#添加普通文本
	def appendText(self,data):
		self.buffer+=data

	#添加控制命令
	def appendCmd(self,cmd):
		self.buffer+=escStr2RawData(cmd)

	#添加条码,条码宽度现在规定为12位，形如：123456789012
	def appendBarCode(self,code):
		if len(code)>12:
			code = code[0:12]
		if len(code)<12:
			code = "0"*(12-len(code))+code

		tmpCode = code[0:2]+" "+code[2:4]+" "+code[4:6]+" "+code[6:8]+" "+code[8:10]+" "+code[10:]
		#print tmpCode
		self.appendCmd("esc @")
		self.appendCmd("27 97 2")
		self.appendCmd("GS w 3")
		self.appendCmd("GS h 120")
		self.appendCmd("29 72 2")
		#GS k 73 8中的8指后面8个字节被视为条码数据，如果数据过多，超过打印宽度则不会打印出条码
		self.appendCmd("GS k 73 8 123 67 "+tmpCode.strip())
		self.appendText('\n')

	#添加列表数据
	def appendList(self,intlist):
		self.buffer+=list2RawData(intlist)

	#将缓冲区中的数据发送到打印机
	def printTask(self):
		dataFile = workingDir +'\\data\\'+str(uuid.uuid1())+'.txt'
		#准备将打印数据写入数据文件
		dataHandle =open(dataFile,'w')
		#控制命令 打印条码
		dataHandle.write(self.buffer)
		dataHandle.close()
		#让usb打印机执行打印作业
		cmdLine = exeFile +" "+ self.printerName +" "+ dataFile
		os.system(cmdLine)
		os.remove(dataFile)    #删除临时文件

	#将文件中的数据发送到打印机
	def printFileTask(self,fileName):
		dataFile = workingDir +'\\data\\'+fileName
		cmdLine = exeFile +" "+ self.printerName +" "+ dataFile
		os.system(cmdLine)

	#当前时刻
	def now(self):
		return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
