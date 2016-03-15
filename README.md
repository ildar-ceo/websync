# Синхронизация файлов по FTP и SFTP

## 
```
[www@php websync]$ websync
Tools for manage web projects. Usage:
  websync downloadftp [project] [host] - download project from FTP
  websync downloadsftp [project] [host] - download project from SFTP
  websync uploadftp [project] [host] - upload project to FTP
  websync showhosts [project] - show hosts
  websync showprojects - show projects
```
## Пример использования:
```
websync downloadftp project1 www.project.ru
websync uploadftp project1 www.project.ru
```

## Процесс установки

```
cd /opt/
git clone https://github.com/vistoyn/websync.git
ln -sf /opt/websync/websync.py /usr/bin/websync
su www
mkdir ~/.websync
cp /opt/websync/settings.example.cfg ~/.websync/settings.cfg
```
