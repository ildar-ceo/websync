# Синхронизация файлов по FTP и SFTP

- websync downloadftp [project] [host] - download project from FTP
- websync downloadsftp [project] [host] - download project from SFTP
- websync uploadftp [project] [host] - upload project to FTP
- websync showhosts [project] - show hosts
- websync showprojects - show projects

## Процесс установки
```
cd /opt/
git clone https://github.com/vistoyn/websync.git
ln -sf /opt/websync/websync.py /usr/bin/websync
su www
mkdir ~/.websync
cp /opt/websync/settings.example.cfg ~/.websync/settings.cfg
```
