#!/usr/bin/env python3

import sys

from bs4 import BeautifulSoup
from functions import read_processed
from functions import load_json
from functions import read_raw
from functions import parse_package
from functions import print_package
from functions import get_version
from functions import get_script
from functions import get_bin_script
from functions import parse_perl_modules
from functions import package_clone
from functions import find_package
from functions import get_package_sections
from functions import get_section
import mate
import kde_apps
import os

import json
import shutil

book_dir = '/home/chandrakant/aryalinux/books/blfs'
out_dir = '/home/chandrakant/aryalinux/aryalinux/applications'
patches_file = '/home/chandrakant/aryalinux/patches/patches.list'

with open(patches_file, 'w') as fp:
	fp.write('')

if len(sys.argv) < 2:
	print('Please provide version')
	exit()
else:
	version = sys.argv[1]

unwanted_chapters = ['preface', 'introduction', 'appendices']
unwanted_pages = {
	'postlfs': ['profile', 'postlfs', 'config', 'bootdisk', 'console-fonts', 'firmware', 'devices', 'skel', 'users', 'vimrc', 'logon', 'security', 'vulnerabilities', 'filesystems', 'initramfs', 'editors', 'shells', 'virtualization', 'aboutlvm', 'firewall', 'others', 'raid'],
	'general': ['general', 'genlib', 'graphlib', 'genutils', 'sysutils', 'prog', 'other-tools', 'ojdk-conf', 'svnserver'],
	'basicnet': ['basicnet', 'connect', 'advanced-network', 'netprogs', 'othernetprogs', 'netutils', 'netlibs', 'textweb', 'mailnews', 'othermn'],
	'kde': ['add-pkgs', 'introduction', 'kdeintro'],
	'x': ['dm-introduction', 'icons-introduction', 'introduction', 'other-wms', 'tuning-fontconfig', 'xorg-config', 'xorg7', 'TTF-and-OTF-fonts'],
	'pst': ['tex-path']
}

unwanted_scripts = ['ttf-and-otf-fonts']

additional_packages = load_json('config/additional_packages.json')
additional_dependencies = load_json('config/additional_dependencies.json')
additional_downloads = load_json('config/additional_downloads.json')
cloned_packages = load_json('config/cloned_packages.json')
binary_packages = load_json('config/bin_packages.json')

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
	package = parse_package(book_dir + '/' + link.attrs['href'], version, patches_file)
	packages.append(package)

# Modification of php commands
with open('config/templates/phpconfig') as fp:
	php_configure = fp.read()
for p in packages:
	if p['name'] == 'php':
		needle = p['commands'][p['commands'].index('./configure'): p['commands'].index('make') + 4]
		p['commands'] = p['commands'].replace(needle, php_configure)

# Fetching sections
friendly_section_names = {
	'postlfs/config': 'Configuration',
	'security': 'Security',
	'filesystems': 'Filesystems',
	'editors': 'Editors',
	'shells': 'Shells',
	'virtualization': 'Virtualization',
	'general/': 'Miscellaneous',
	'basicnet/': 'Networking',
	'server/': 'Servers',
	'x/': 'X-Server',
	'kde/': 'KDE',
	'gnome/': 'Gnome',
	'xfce/': 'XFCE',
	'xsoft/': 'Office Productivity',
	'multimedia/': 'Multimedia',
	'pst/': 'Printing and Typesetting'
}

sections_dict = get_package_sections(book_dir)
sections = sections_dict.keys()

# Generate packages in the book
for p in packages:
	get_section(p, sections_dict, friendly_section_names)
	if p['name'] == 'krameworks5':
		frameworks = p
	if p['name'] == 'plasma-all':
		plasma_all = p
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

if 'fetch-mate' in sys.argv:
	# Generate mate packages
	mate_packages = mate.get_packages()
	for package in mate_packages:
		with open(out_dir + '/' + package['name'] + '.sh', 'w') as fp:
			script = get_script(package)
			fp.write(script)
else:
	print('Not fetching mate packages.')

if 'fetch-kde-apps' in sys.argv:
	kde_packages = kde_apps.get_packages(sys.argv[sys.argv.index('fetch-kde-apps') + 1], plasma_all, frameworks)
	for package in kde_packages:
		with open(out_dir + '/' + package['name'] + '.sh', 'w') as fp:
			script = get_script(package)
			fp.write(script)
else:
	print('Not fetching kde apps.')

# Generate cloned packages
for name, clone_details in cloned_packages.items():
	package = package_clone(find_package(packages, name), clone_details['name'], clone_details['deps'])
	with open(out_dir + '/' + package['name'] + '.sh', 'w') as fp:
		script = get_script(package)
		fp.write(script)

# Generate binary packages
for package in binary_packages:
	with open(out_dir + '/' + package['name'] + '-bin.sh', 'w') as fp:
		script = get_bin_script(package)
		fp.write(script)

for f in unwanted_scripts:
	if os.path.exists(out_dir + '/' + f + '.sh'):
		os.remove(out_dir + '/' + f + '.sh')


for f in os.listdir('app-scripts'):
	shutil.copyfile('app-scripts/' + f, out_dir + '/' + f)

