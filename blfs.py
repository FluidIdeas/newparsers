#!/usr/bin/env python3

from bs4 import BeautifulSoup
from functions import read_processed
from functions import read_raw
from functions import parse_package

book_dir = '/home/chandrakant/aryalinux/books/blfs'
out_dir = '/home/chandrakant/aryalinux/aryalinux/applications'

unwanted_chapters = ['preface', 'introduction', 'appendices']
unwanted_pages = {
	'postlfs': ['postlfs', 'config', 'bootdisk', 'console-fonts', 'firmware', 'devices', 'skel', 'users', 'vimrc', 'logon', 'security', 'vulnerabilities', 'filesystems', 'initramfs', 'editors', 'shells', 'virtualization'],
	'general': ['general', 'genlib', 'graphlib', 'genutils', 'sysutils', 'prog', 'other-tools'],
	'basicnet': ['basicnet', 'connect', 'advanced-network', 'netprogs', 'othernetprogs', 'netutils', 'netlibs', 'textweb', 'mailnews']
}

packages = list()

document = BeautifulSoup(read_processed(book_dir + '/index.html'), 'html.parser')
links = document.select('li.sect1 a[href]')
for link in links:
	process = True
	for chapter, pages in unwanted_pages.items():
		if link.attrs['href'].split('/')[-1].replace('.html', '') in pages:
			process = False
			break
	if not process:
		continue
	package = parse_package(book_dir + '/' + link.attrs['href'])
	packages.append(package)

for p in packages:
	if p['name'] == 'mariadb':
		print(p)
