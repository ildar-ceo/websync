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
cd /opt/
git clone https://github.com/vistoyn/websync.git
ln -sf /opt/websync/websync.py /usr/local/bin/websync
su www
mkdir ~/.websync
cp /opt/websync/settings.example.cfg ~/.websync/settings.cfg
```
