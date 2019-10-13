#!/usr/bin/env python3

import subprocess
from bs4 import BeautifulSoup
from decimal import Decimal

mate_packages = 'libidl libart intltool libtool yelp mate-common mate-desktop libmatekbd libmatewnck libmateweather mate-icon-theme caja marco mate-settings-daemon mate-session-manager mate-menus mate-panel mate-control-center plymouth mate-screensaver mate-terminal caja caja-extensions caja-dropbox pluma galculator eom engrampa atril mate-utils murrine-gtk-engine gnome-themes-standard mate-system-monitor mate-power-manager marco mozo mate-backgrounds mate-media ModemManager usb_modeswitch compton libmatemixer'

def download(url, file):
	proc = subprocess.Popen('wget ' + url + ' -O ' + file + ' &> /dev/null', shell=True)
	proc.communicate()
	proc.wait()

def collect_anchors(url):
	download(url, 'tmpfile')
	a_list = list()
	with open('tmpfile') as fp:
		doc = BeautifulSoup(fp.read(), features="lxml")
		anchors = doc.select('a')
		for anchor in anchors:
			a_list.append(anchor)
	return a_list

def get_version(tarball):
	s = tarball[tarball.rindex('-') + 1: tarball.rindex('.tar')]
	return s.split('.')

def get_max(version_list):
	if len(version_list[0]) == 1:
		versions = list()
		for v in version_list:
			versions.append(int(v[0]))
		versions.sort()
		return str(versions[len(versions) - 1])
	else:
		all_first = list()
		for version in version_list:
			all_first.append(int(version[0]))
		all_first.sort()
		all_remains = list()
		for version in version_list:
			if int(version[0]) == all_first[len(all_first) - 1]:
				all_remains.append(version[1:])
		return str(all_first[len(all_first) - 1]) + '.' + get_max(all_remains)

def latest(tarballs):
	all_versions = list()
	for tarball in tarballs:
		if '.news' in tarball:
			continue
		version = get_version(tarball)
		all_versions.append(version)
	return get_max(all_versions)

def get_links():
	discards = ['../', 'SHA1SUMS']
	pkg_root='https://pub.mate-desktop.org/releases/'
	package_details = dict()

	anchors = collect_anchors(pkg_root)
	for anchor in anchors:
		if anchor.text != '../' and anchor.text != 'themes/':
			package_details[anchor.text.replace('/', '')] = list()

	for key, value in package_details.items():
		# key is the version in the downloads page...
		anchors = collect_anchors(pkg_root + key + '/')
		for anchor in anchors:
			if anchor['href'] not in discards:
				package_details[key].append(anchor['href'])

	all_versions = dict()
	for package in mate_packages.split():
		# package is a component of mate-desktop-environment
		for key, value in package_details.items():
			# key is version number
			# value is the list of tarballs
			for v in value:
				if package in v and v.index(package) == 0:
					# we found a mate component package in the list for a particular version
					if not package in all_versions:
						all_versions[package] = list()
					# v is the tarball
					#print(v)
					all_versions[package].append(v)

	links = dict()
	for key, value in all_versions.items():
		# Here we can replace all_versions[key] with value
		version = latest(all_versions[key])
		if len(version.split('.')) == 2:
			directory = version
		else:
			directory = version[0:version.rindex('.')]
		links[key] = pkg_root + directory + '/' + key + '-' + latest(all_versions[key]) + '.tar.xz'

	proc = subprocess.Popen('rm tmpfile', shell=True)
	proc.communicate()
	proc.wait()
	return links

def get_packages():
	mate_packages = list()
	links = get_links()
	for name, link in links.items():
		package = dict()
		package['name'] = name
		package['download_urls'] = [link]
		package['tarball'] = link[link.rindex('/') + 1:]
		package['version'] = package['tarball'].replace(name + '-', '').replace('.tar.xz', '')
		if package['name'] == 'mate-power-manager':
			package['commands'] = "./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --disable-static --without-keyring --with-gtk=3.0 &&\nmake\n\nsudo make install"
		elif package['name'] == 'mate-backgrounds':
			package['commands'] = "mkdir -pv build\ncd build\nmeson --prefix=/usr&&\nninja\n\nsudo ninja install"
		else:
			package['commands'] = "./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --disable-static &&\nmake\n\nsudo make install"
		package['dependencies'] = []
		mate_packages.append(package)
	return mate_packages

