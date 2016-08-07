# Синхронизация файлов по FTP и SFTP

## Возможности
- скачивать/закачивать рекурсивно файлы и папки по `FTP/SFTP`
- прописать пароли и пути к проектам в `settings.cfg`
- список исключения файлов и папок

## Пример использования
- `websync downloadftp [project] [host]` - download project from FTP
- `websync downloadsftp [project] [host]` - download project from SFTP
- `websync uploadftp [project] [host]` - upload project to FTP
- `websync showhosts [project]` - show hosts
- `websync showprojects` - show projects

## Процесс установки
```
sudo pypi3.5 install websync
```

## Конфиг

```
ftp:
	test: 
		host: test-host
		port: 22
		user: ftp
		pass: 123
projects:
	testproject:
		local_path: /www/testproject/
		ftp:
			test-host:
				download: /www/testproject
				upload: /www/testproject
		exclude:
			- ^.hg
			- ^.git
			- ^cache
			- ^vendor
```
