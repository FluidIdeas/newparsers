#!/usr/bin/env python3

from bs4 import BeautifulSoup
from functions import read_processed
from functions import load_json
from functions import read_raw
from functions import parse_package
from functions import print_package
from functions import get_version
from functions import get_script
from functions import parse_perl_modules

import json

book_dir = '/home/chandrakant/aryalinux/books/blfs'
out_dir = '/home/chandrakant/aryalinux/aryalinux/applications'

unwanted_chapters = ['preface', 'introduction', 'appendices']
unwanted_pages = {
	'postlfs': ['profile', 'postlfs', 'config', 'bootdisk', 'console-fonts', 'firmware', 'devices', 'skel', 'users', 'vimrc', 'logon', 'security', 'vulnerabilities', 'filesystems', 'initramfs', 'editors', 'shells', 'virtualization'],
	'general': ['general', 'genlib', 'graphlib', 'genutils', 'sysutils', 'prog', 'other-tools'],
	'basicnet': ['basicnet', 'connect', 'advanced-network', 'netprogs', 'othernetprogs', 'netutils', 'netlibs', 'textweb', 'mailnews']
}

additional_packages = load_json('config/additional_packages.json')
additional_dependencies = load_json('config/additional_dependencies.json')
additional_downloads = load_json('config/additional_downloads.json')

packages = list()

document = BeautifulSoup(read_processed(book_dir + '/index.html'), 'html.parser')
links = document.select('li.sect1 a[href]')

for link in links:
	if 'perl-modules.html' in link.attrs['href'] or 'perl-deps.html' in link.attrs['href'] or 'python-modules.html' in link.attrs['href'] or 'x7driver.html' in link.attrs['href']:
		packages.extend(parse_perl_modules(book_dir + '/' + link.attrs['href']))
		continue
	process = True
	for unwanted_chapter in unwanted_chapters:
		if link.attrs['href'].split('/')[0] == unwanted_chapter:
			process = False
			break
	if process == False:
		continue
	for chapter, pages in unwanted_pages.items():
		if link.attrs['href'].split('/')[-1].replace('.html', '') in pages:
			process = False
			break
	if not process:
		continue
	package = parse_package(book_dir + '/' + link.attrs['href'])
	packages.append(package)

# Generate packages in the book
for p in packages:
	if p['name'] in additional_dependencies:
		p['dependencies'].extend(additional_dependencies[p['name']])
	if p['name'] in additional_downloads:
		p['download_urls'].extend(additional_downloads[p['name']])
	if 'commands' in p:
		with open(out_dir + '/' + p['name'] + '.sh', 'w') as fp:
			script = get_script(p)
			fp.write(script)

# Generate additional packages
for package in additional_packages:
	with open(out_dir + '/' + package['name'] + '.sh', 'w') as fp:
		script = get_script(package)
		fp.write(script)

