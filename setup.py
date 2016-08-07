#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""
Инструкции:

python3 setup.py sdist - Сборка пакета
sudo python3 setup.py develop - Установка пакета для разработки
sudo pip3 install dist/websync-0.1.zip - Установка пакета
sudo pip3 uninstall websync - Удаление пакета
python3 setup.py register - Зарегистрировать пакет в pypi
python3 setup.py sdist upload - Залить на сервер

Список классификации:
https://pypi.python.org/pypi?%3Aaction=list_classifiers

"""

from setuptools import setup, find_packages
from os.path import join, dirname

PACKAGE = "websync"
NAME = "websync"
LICENSE = "Apache License Version 2.0"
URL = "https://github.com/vistoyn/websync"
DESCRIPTION = __import__(PACKAGE).__description__
AUTHOR = __import__(PACKAGE).__author__
AUTHOR_EMAIL = __import__(PACKAGE).__email__
VERSION = __import__(PACKAGE).__version__

setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=open(join(dirname(__file__), 'DESCRIPTION.rst')).read(),
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	license=LICENSE,
	url = URL,
	packages=find_packages(),
	include_package_data = True,
	scripts=[
		'scripts/websync'
	],
	install_requires=[
	],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.5',
		'Topic :: Internet',
		'Topic :: Utilities',
	],
)