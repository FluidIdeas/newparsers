#!/usr/bin/env python3

import subprocess
from bs4 import BeautifulSoup
from decimal import Decimal

mate_packages = 'libidl libart intltool libtool yelp mate-common mate-desktop libmatekbd libmatewnck libmateweather mate-icon-theme caja marco mate-settings-daemon mate-session-manager mate-menus mate-panel mate-control-center plymouth mate-screensaver mate-terminal caja caja-extensions caja-dropbox pluma galculator eom engrampa atril mate-utils murrine-gtk-engine mate-themes-gtk3 gnome-themes-standard mate-system-monitor mate-power-manager marco mozo mate-backgrounds mate-media ModemManager usb_modeswitch compton'

def download(url, file):
	proc = subprocess.Popen('wget ' + url + ' -O ' + file, shell=True)
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

def latest(tarballs):
	versions = dict()
	for tarball in tarballs:
		version = get_version(tarball)
		if int(version[0]) in versions:
			if int(version[1]) in versions[int(version[0])]:
				versions[int(version[0])][int(version[1])].append(int(version[2]))
			else:
				versions[int(version[0])][int(version[1])] = list()
		else:
			versions[int(version[0])] = dict()
	for major, minors in versions.items():
		for minor, builds in minors.items():
			builds.sort()
	major_list = list(versions.keys())
	major_list.sort()
	major = major_list[-1]
	minor_list = list(versions[major].keys())
	minor_list.sort()
	minor = minor_list[-1]
	build_list = versions[major][minor]
	build_list.sort()
	if len(build_list) > 0:
		build = build_list[-1]
	else:
		build = None
	retval = ''
	if major != None:
		retval = retval + str(major)
	if minor != None:
		retval = retval + '.' + str(minor)
	if build != None:
		retval = retval + '.' + str(build)
	return retval

def get_links():
	discards = ['../', 'SHA1SUMS']
	pkg_root='https://pub.mate-desktop.org/releases/'
	package_details = dict()

	anchors = collect_anchors(pkg_root)
	for anchor in anchors:
		if anchor.text != '../' and anchor.text != 'themes/':
			package_details[anchor.text.replace('/', '')] = list()

	for key, value in package_details.items():
		anchors = collect_anchors(pkg_root + key + '/')
		for anchor in anchors:
			if anchor['href'] not in discards:
				package_details[key].append(anchor['href'])

	all_versions = dict()
	for package in mate_packages.split():
		for key, value in package_details.items():
			for v in value:
				if package in v and v.index(package) == 0:
					if not package in all_versions:
						all_versions[package] = list()
					all_versions[package].append(v)

	links = dict()
	for key, value in all_versions.items():
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
		package['commands'] = "./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --disable-static &&\nmake\n\nsudo make install"
		package['dependencies'] = []
		mate_packages.append(package)
	return mate_packages

