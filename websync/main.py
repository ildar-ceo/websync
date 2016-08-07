#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# Author  : Bikmamatov Ildar
# Module  : Tools for web projects
# File    : websync.py
# Version : 1.0
# Example :
#	web downloadftp [project] [host]
#	web uploadftp [project] [host]
#
import os, json, re, sys, subprocess, yaml
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
	CFG = yaml.load(data)
	return CFG
	
global CFG
path = os.path.join(os.environ['HOME'] + '/.websync/', 'settings.cfg')
#CFG = loadJsonFromFile(path)
CFG = loadYamlFromFile(path)

def outUsage():
	print ('Tools for manage web projects. Usage:')
	print ('  websync downloadftp [project] [host] - download project from FTP')
	print ('  websync downloadsftp [project] [host] - download project from SFTP')
	print ('  websync uploadftp [project] [host] - upload project to FTP')
	print ('  websync showhosts [project] - show hosts')
	print ('  websync showprojects - show projects')
		
		
def downloadftp(project, host):
	global CFG
	
	project = str(project)
	host = str(host)
	ftp = xarr(CFG,'ftp',None,TypeObject)
	ftp_params = xarr(ftp,host,None,TypeObject)
	
	ftp_host = xarr(ftp_params, 'host', None, TypeString)
	ftp_port = xarr(ftp_params, 'port', '22', TypeString)
	ftp_user = xarr(ftp_params, 'user', None, TypeString)
	ftp_pass = xarr(ftp_params, 'pass', None, TypeString)

	projects = xarr(CFG,'projects',None,TypeObject)
	project_CFG = xarr(projects,project,None,TypeObject)
	local_path = xarr(project_CFG,'local_path',None,TypeString)
	download_path = xarr(xarr(xarr(project_CFG, 'ftp', None, TypeObject), host, None, TypeObject), 'download', None, TypeString)
	
	if ftp_params == None or ftp_host == None or ftp_user == None or ftp_pass == None:
		print ('Ftp params for host ' + host + ' is not set ')
		return 0

	if local_path == None:
		print ('Local path for project ' + project + ' is not set ')
		return 0		
	
	if download_path == None:
		print ('Ftp ' + host + ' for project ' + project + ' is not set ')
		return 0			
	
	print ('Скачать по ФТП с сервера '+ConsoleColors.OKBLUE+ftp_host+ConsoleColors.ENDC+' из папки '+ConsoleColors.OKGREEN+download_path+ConsoleColors.ENDC+' в папку ' +ConsoleColors.WARNING+ local_path+ConsoleColors.ENDC)
	
	exclude = xarr(project_CFG,'exclude',None,TypeArray)
	
	if query_yes_no("Вы действительно хотите скачать с FTP данные?", "no"):
	
		import ftputil
		
		# Download some files from the login directory.
		with ftputil.FTPHost(ftp_host, ftp_user, ftp_pass) as host:
			
			def downloadDirectory(source,dest):
				try:
					host.chdir(source)
				except Exception as e:
					return
				
				dirsload=[]
				
				print ("Enter folder " + ConsoleColors.OKBLUE + source + ConsoleColors.ENDC)
				mkdir(dest)
				names = host.listdir(host.curdir)
				for name in names:
					isLink = host.path.islink(name)
					isDir = host.path.isdir(name)
					isFile = host.path.isfile(name)
					stat_result = host.lstat(name)
					
					new_source = source + '/' + name
					new_dest = dest+ '/' + name
					
					ignore=False
					name = new_dest[len(local_path)+1:]
					st_mtime = stat_result.st_mtime
					st_size = stat_result.st_size
					
					for path in exclude:
						if re.search(path, name) != None:
							ignore=True
						pass
					
					if ignore:
						continue
					
					if isLink:
						
						if isDir or isFile:
							print ("Create symlink " + ConsoleColors.OKGREEN + new_source + ConsoleColors.ENDC)
							try:
								#os.symlink(new_dest, stat_result._st_target)
								cmd = "rm -f "+shellescape(new_dest)+" "
								subprocess.call(cmd, shell=True, executable='/bin/bash')
								
								cmd = "ln -sf "+shellescape(stat_result._st_target)+" "+shellescape(new_dest)+" "
								#print (cmd)
								subprocess.call(cmd, shell=True, executable='/bin/bash')
							except Exception as e:
								pass
							
						else:
							print ("Unknown symlink " + ConsoleColors.WARNING + new_source + ConsoleColors.ENDC)
					
					elif isDir:
						dirsload.append((new_source,new_dest,st_mtime))
						
					elif isFile:
						
						ignore=False
						if os.path.exists(new_dest):
							stat = os.stat(new_dest)
							#print (stat.st_size + ' != ' + stat_result.st_size)
							#print (stat)
							#print ((stat.st_size != stat_result.st_size) and (stat.st_mtime != stat_result.st_mtime))
							if (stat.st_size == stat_result.st_size): ignore = True
							#if (stat.st_size == stat_result.st_size) and (stat.st_mtime == stat_result.st_mtime): ignore = True
							
						if ignore:
							continue
					
						print ("Download file " + ConsoleColors.OKGREEN + new_source + ConsoleColors.ENDC)
						host.download(new_source, new_dest)
						os.utime(new_dest, (0, st_mtime))
					
					else:
						print ("Unknown file type " + ConsoleColors.WARNING + new_source + ConsoleColors.ENDC)
				
				for dir in dirsload:
					new_source = dir[0]
					new_dest = dir[1]
					st_mtime = dir[2]
					downloadDirectory(new_source, new_dest)
					os.utime(new_dest, (0, st_mtime))

			downloadDirectory(download_path, local_path)
		return 1
	else:
		print ('Отмена')
		
	return 0

	
def uploadftp(project, host):
	global CFG
	
	project = str(project)
	host = str(host)
	ftp = xarr(CFG,'ftp',None,TypeObject)
	ftp_params = xarr(ftp,host,None,TypeObject)
	
	ftp_host = xarr(ftp_params, 'host', None, TypeString)
	ftp_port = xarr(ftp_params, 'port', '22', TypeString)
	ftp_user = xarr(ftp_params, 'user', None, TypeString)
	ftp_pass = xarr(ftp_params, 'pass', None, TypeString)

	projects = xarr(CFG,'projects',None,TypeObject)
	project_CFG = xarr(projects,project,None,TypeObject)
	local_path = xarr(project_CFG,'local_path',None,TypeString)
	upload_path = xarr(xarr(xarr(project_CFG, 'ftp', None, TypeObject), host, None, TypeObject), 'download', None, TypeString)
	
	if ftp_params == None or ftp_host == None or ftp_user == None or ftp_pass == None:
		print ('Ftp params for host ' + host + ' is not set ')
		return 0

	if local_path == None:
		print ('Local path for project ' + project + ' is not set ')
		return 0		
	
	if upload_path == None:
		print ('Ftp ' + host + ' for project ' + project + ' is not set ')
		return 0			
	
	print ('Закачать на ФТП сервера '+ConsoleColors.OKBLUE+ftp_host+ConsoleColors.ENDC+' из папки '+ConsoleColors.OKGREEN+local_path+ConsoleColors.ENDC+' в папку фтп ' +ConsoleColors.WARNING+ upload_path+ConsoleColors.ENDC)
	
	exclude = xarr(project_CFG,'exclude',None,TypeArray)
	
	if query_yes_no("Вы действительно хотите закачать на FTP данные?", "no"):
	
		import ftputil, os
		
		# Download some files from the login directory.
		with ftputil.FTPHost(ftp_host, ftp_user, ftp_pass) as host:	
			
			def uploadDirectory(source, dest):
				try:
					host.makedirs(dest)
					host.chdir(dest)
					pass
				except Exception as e:
					return
				
				dirsload=[]
				print ("Enter folder " + ConsoleColors.OKBLUE + dest + ConsoleColors.ENDC)
				
				for name in os.listdir(source):
					#print (name)
					new_source = source + '/' + name
					new_dest = dest+ '/' + name	
				
					isLink = os.path.islink(new_source)
					isDir = os.path.isdir(new_source)
					isFile = os.path.isfile(new_source)
					stat_result = os.stat(new_source)					
					st_mtime = stat_result.st_mtime
					st_size = stat_result.st_size
					
					ignore=False
					
					full_name = new_dest[len(upload_path)+1:]
					for path in exclude:
						if re.search(path, full_name) != None:
							ignore=True
						pass
					
					if ignore:
						continue
					
					if isLink:
					
						if isDir or isFile:
							#print ("Create symlink " + ConsoleColors.OKGREEN + new_source + ConsoleColors.ENDC)
							pass
						else:
							#print ("Unknown symlink " + ConsoleColors.WARNING + new_source + ConsoleColors.ENDC)
							pass
					
					elif isDir:
						dirsload.append((new_source,new_dest,st_mtime))
					
					elif isFile:
						ignore=False
						if host.path.exists(new_dest):
							stat = host.lstat(new_dest)
							#print (stat.st_size + ' != ' + stat_result.st_size)
							#print (stat)
							#print ((stat.st_size != stat_result.st_size) and (stat.st_mtime != stat_result.st_mtime))
							if (stat.st_size == stat_result.st_size): ignore = True
							#if (stat.st_size == stat_result.st_size) and (stat.st_mtime == stat_result.st_mtime): ignore = True
							
						if ignore:
							continue
					
						print ("Upload file to " + ConsoleColors.OKGREEN + new_dest + ConsoleColors.ENDC)
						#print (new_dest)
						host.upload(new_source, new_dest)
						#host.utime(new_dest, (0, st_mtime))
					
					else:
						print ("Unknown file type " + ConsoleColors.WARNING + new_source + ConsoleColors.ENDC)

				for dir in dirsload:
					new_source = dir[0]
					new_dest = dir[1]
					st_mtime = dir[2]
					uploadDirectory(new_source, new_dest)
					#host.utime(new_dest, (0, st_mtime))					
				
			uploadDirectory(local_path, upload_path)
			
		return 1
	else:
		print ('Отмена')
		
	return 0	
	
def showProjects():
	global CFG
	projects = xarr(CFG,'projects',{},TypeObject)
	print ('Projects: ')
	for project in projects:
		print ('  ' + project)	
	
def showHosts(project):
	global CFG
	projects = xarr(CFG,'projects',None,TypeObject)
	project_CFG = xarr(projects,project,None,TypeObject)
	
	ftp = xarr(project_CFG,'ftp',{},TypeObject)
	sftp = xarr(project_CFG,'sftp',{},TypeObject)
	
	print ('FTP: ')
	for f in ftp:
		print ('  ' + f)
		
	print ('SFTP: ')
	for f in sftp:
		print ('  ' + f)
	
	
	
# Главная программа
def main():
	command = xarr(sys.argv, 1)
	if command == 'downloadftp':
		project = xarr(sys.argv, 2)
		host = xarr(sys.argv, 3)
		
		if (project != None) and (host != None):
			downloadftp(project, host)
		elif (project != None)  and (host == None):
			print ('Tools for manage web projects. Usage:')
			print ('  websync downloadftp [project] [host]')
			showHosts(project)		
		else:
			print ('Tools for manage web projects. Usage:')
			print ('  websync downloadftp [project] [host]')
			showProjects()	
		
	elif command == 'uploadftp':
		project = xarr(sys.argv, 2)
		host = xarr(sys.argv, 3)
		
		if (project != None) and (host != None):
			uploadftp(project, host)
		elif (project != None)  and (host == None):
			print ('Tools for manage web projects. Usage:')
			print ('  websync uploadftp [project] [host]')
			showHosts(project)		
		else:
			print ('Tools for manage web projects. Usage:')
			print ('  websync uploadftp [project] [host]')
			showProjects()	
		
	elif command == 'showprojects':
		showProjects()

	elif command == 'showhosts':
		project = xarr(sys.argv, 2)
		
		if project != None:
			showHosts(project)
			
		else:
			print ('Tools for manage web projects. Usage:')
			print ('  websync showhosts [project] - show hosts')
			projects = xarr(CFG,'projects',{},TypeObject)
			print ('Projects: ')
			for project in projects:
				print ('  ' + project)
			
	else:
		outUsage()
#!enddef main