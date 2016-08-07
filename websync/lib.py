# -*- coding: utf-8 -*- 
# Author : Bikmamatov Ildar
# Module : django_ext
# Description : Функции для модуля websync.py

import os, json, re, sys, subprocess, time, traceback
import asyncio, yaml
#sys.path.insert(0, os.getcwd())
import libftp as aioftp
from .dict import *

def loadJsonFromString(data):
	#data = re.sub(r'[\x00-\x20]+', ' ', data)
	#data = re.sub(r'\s+', ' ', data)	
	data = data.strip()
	
	data = re.sub(r',}', '}', data)	
	
	#print (data)
	json_data = json.loads(data)
	return json_data

def loadJsonFromFile(file_name):
	file = open(path, 'rb')
	data = file.read().decode('utf-8')
	file.close()
	return loadJsonFromString(data)	

def loadYamlFromFile(path):
	file = open(path, 'rb')
	data = file.read().decode('utf-8')
	file.close()
	data = re.sub(r'\t', '  ', data)	
	cfg = yaml.load(data)
	return cfg
	
def getFtpParamsByHost(cfg, host):
	host = str(host)
	ftp = xarr(cfg,'ftp',None,TypeObject)
	ftp_params = xarr(ftp,host,None,TypeObject)
	return ftp_params

def getProjectParams(cfg, project):
	project = str(project)
	projects = xarr(cfg,'projects',None,TypeObject)
	project_CFG = xarr(projects,project,None,TypeObject)
	return project_CFG
	
def getProjectFtpParamsByHost(cfg, project, host):
	project_params = getProjectParams(cfg, project)
	project_ftp_params = xarr(project_params, 'ftp', None, TypeObject)
	ftp_host_params = xarr(project_ftp_params, host, None, TypeObject)
	return ftp_host_params
	
# ---- Работа с ФТП ----

async def connect(host, port, username, password):
	ftp = aioftp.Client()
	await ftp.connect(host)
	await ftp.login(username, password)
	return ftp

class BaseDownloadClass:
	def setConfig (self, config):
		self.config = config
	
	def __init__(self, *args, **kwargs):
		self.config = None
		self.host = None
		self.port = None
		self.username = None
		self.password = None
		self.exclude = None
		self.localPath = None
		self.downloadPath = None
	
class DownloadFtp(BaseDownloadClass):
	
	def __init__(self, *args, **kwargs):
		self.isStop = asyncio.Event()
		self.isStop.clear()
		self.future = None
		self.loop = None
		self.downloadQueue = asyncio.Queue()
		self.downloadTasksCount=0
	
	async def listTreeRecursive(self, ftp, path):
		list_dir=[]
		
		print ("Listing folder " + ConsoleColors.OKBLUE + path + ConsoleColors.ENDC)
		tmp_path = str(path)[len(self.downloadPath):]
		upload_path = joinPath(self.localPath, tmp_path)
		mkdir(upload_path, isFile=False)
		
		for path, info in (await ftp.list(path, recursive=False)):
			path = str(path)
			type = info.get('type')
			
			#print (path)
			#print (info)
			
			if type == 'dir':
				list_dir.append(path)
			elif type == 'file':
				await self.downloadQueue.put( ('file',path) )
			elif 'symlink' in type:
				await self.downloadQueue.put( ('symlink',path) )
			
			pass
			
		for path in list_dir:
			await self.listTreeRecursive(ftp, path)
	
	async def listTree(self, path):
		try:
			ftp = await connect(self.host, self.port, self.username, self.password)
			await self.listTreeRecursive(ftp, path)
			await ftp.quit()
		except Exception as e:
			traceback.print_exc()
		self.isStop.set()
		
	async def downloadFiles(self):
		try:
	
			ftp = await connect(self.host, self.port, self.username, self.password)
			self.downloadTasksCount = self.downloadTasksCount + 1
			currentIndex = self.downloadTasksCount;
			while True:
				try:
					(type, download_path) = self.downloadQueue.get_nowait()
					
					if type == 'file':
						path = str(download_path)[len(self.downloadPath):]
						upload_path = joinPath(self.localPath, path)
						
						print ('['+str(currentIndex)+"] Download file " + ConsoleColors.OKGREEN + download_path + ConsoleColors.ENDC)
						#await ftp.download(download_path, upload_path, write_into=True)
					elif type == 'symlink':
						
						info = await ftp.ls_stat(download_path)
						print (info)
						
						info = await ftp.stat(download_path)
						print (info)
						
						pass
					
				except asyncio.QueueEmpty:
					#print (self.isStop.is_set())
					if self.isStop.is_set():
						break;
					await asyncio.sleep(1)
				except Exception as e:
					print ('['+str(currentIndex)+'] Error: ' + str(e))
					traceback.print_exc()
				
			#print ('exit from downloadFiles')
			await ftp.quit()
			pass
		
		except Exception as e:
			traceback.print_exc()
	
	async def mainLoop(self):
		tasks=[]
		tasks.append(asyncio.ensure_future(self.listTree(self.downloadPath)))
		for i in range(0,5):	
			tasks.append(asyncio.ensure_future(self.downloadFiles()))
		await asyncio.wait(tasks)
	
	async def gotResult(self, future):
		#future.result()
		await asyncio.sleep(2.0)
		self.loop.stop()
	
	def run(self, project, host):
		
		ftp_params = getFtpParamsByHost(self.config, host)
		project_params = getProjectParams(self.config, project)
		project_ftp_params = getProjectFtpParamsByHost(self.config, project, host)	
		
		self.host = xarr(ftp_params, 'host', None, TypeString)
		self.port = xarr(ftp_params, 'port', '22', TypeString)
		self.username = xarr(ftp_params, 'user', None, TypeString)
		self.password = xarr(ftp_params, 'pass', None, TypeString)
		self.exclude = xarr(project_params,'exclude',None,TypeArray)
		self.localPath = xarr(project_params,'local_path',None,TypeString)
		self.downloadPath = xarr(project_ftp_params, 'download', None, TypeString)
		
		if self.host == None or self.username == None or self.password == None:
			print ('Ftp params for host ' + host + ' is not set ')
			return 0

		if self.localPath == None:
			print ('Local path for project ' + project + ' is not set ')
			return 0		
		
		if self.downloadPath == None:
			print ('Ftp ' + host + ' for project ' + project + ' is not set ')
			return 0
		
		print ('Скачать по ФТП с сервера '+ConsoleColors.OKBLUE+self.host+ConsoleColors.ENDC+' из папки '+ConsoleColors.OKGREEN+self.downloadPath+ConsoleColors.ENDC+' в папку ' +ConsoleColors.WARNING+self.localPath+ConsoleColors.ENDC)
		
		#if query_yes_no("Вы действительно хотите скачать с FTP данные?", "no"):
		if True:
			
			self.loop = asyncio.get_event_loop()
			self.loop.run_until_complete(self.mainLoop())
			
			
			"""
			#asyncio.wait(tasks)
			self.future = asyncio.Future()
			self.future.add_done_callback(self.gotResult)
			tasks = [
				asyncio.ensure_future(self.downloadFiles()),
				asyncio.ensure_future(self.mainLoop())
			]
			
			#asyncio.wait(tasks)
			try:
				self.loop.run_forever()
			finally:
				self.loop.close()
			#loop.run_until_complete(self.main_loop())
			"""
			
			print ('End!')
			
			pass
		
		return 1
	