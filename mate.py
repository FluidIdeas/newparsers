#!/usr/bin/env python3

import subprocess
from bs4 import BeautifulSoup
from decimal import Decimal

mate_packages = 'libidl libart intltool libtool yelp mate-common mate-desktop libmatekbd libmatewnck libmateweather mate-icon-theme caja marco mate-settings-daemon mate-session-manager mate-menus mate-panel mate-control-center plymouth mate-screensaver mate-terminal caja caja-extensions caja-dropbox pluma galculator eom engrampa atril mate-utils murrine-gtk-engine gnome-themes-standard mate-system-monitor mate-power-manager marco mozo mate-backgrounds mate-media ModemManager usb_modeswitch compton libmatemixer mate-calc mate-notification-daemon mate-applets'
mate_sections = {
	"atril": "Mate Desktop Applications",
	"caja-dropbox": "Mate Desktop",
	"caja-extensions": "Mate Desktop",
	"caja":"Mate Desktop Applications",
	"engrampa":"Mate Desktop Applications",
	"eom": "Mate Desktop Applications",
	"libmatekbd": "Mate Desktop",
	"libmatemixer": "Mate Desktop",
	"libmateweather": "Mate Desktop",
	"libmatewnck": "Mate Desktop",
	"marco": "Mate Desktop",
	"mate-backgrounds": "Mate Desktop",
	"mate-common": "Mate Desktop",
	"mate-control-center": "Mate Desktop",
	"mate-desktop": "Mate Desktop",
	"mate-icon-theme": "Mate Desktop",
	"mate-media": "Mate Desktop",
	"mate-menus": "Mate Desktop",
	"mate-panel": "Mate Desktop",
	"mate-power-manager": "Mate Desktop",
	"mate-screensaver": "Mate Desktop",
	"mate-session-manager": "Mate Desktop",
	"mate-settings-daemon": "Mate Desktop",
	"mate-system-monitor": "Mate Desktop",
	"mate-terminal": "Mate Desktop",
	"mate-utils": "Mate Desktop",
	"mozo": "Mate Desktop Applications",
	"pluma": "Mate Desktop Applications",
	"mate-calc": "Mate Desktop Applications",
	"mate-notification-daemon": "Mate Desktop",
	"mate-applets": "Mate Desktop"
}
mate_descriptions = {
	"atril": "Atril is a document viewer capable of displaying multiple and single page document formats like PDF and Postscript.",
	"caja-dropbox": "Dropbox extension for Caja file manager",
	"caja-extensions": "Set of extensions for Caja, the MATE file manager",
	"caja":"Caja, the file manager for the MATE desktop",
	"engrampa":"A file archiver for MATE",
	"eom": "An image viewer for MATE",
	"libmatekbd": "Keyboard management library",
	"libmatemixer": "Mixer library for MATE Desktop",
	"libmateweather": "Library to access weather information from online services",
	"libmatewnck": "Mate Desktop",
	"marco": "MATE default window manager",
	"mate-backgrounds": "This module contains a set of backgrounds packaged with the MATE desktop.",
	"mate-common": "Common scripts and macros to develop with MATE",
	"mate-control-center": "Utilities to configure the MATE desktop",
	"mate-desktop": "Library with common API for various MATE modules",
	"mate-icon-theme": "MATE default icon theme",
	"mate-media": "Media tools for MATE",
	"mate-menus": "Library for the Desktop Menu freedesktop.org specification",
	"mate-panel": "MATE panel",
	"mate-power-manager": "Power management tool for the MATE desktop",
	"mate-screensaver": "MATE screen saver and locker",
	"mate-session-manager": "MATE session manager",
	"mate-settings-daemon": "MATE settings daemon",
	"mate-system-monitor": "Process viewer and system resource monitor for MATE",
	"mate-terminal": "The MATE Terminal Emulator",
	"mate-utils": "MATE Utilities for the MATE Desktop",
	"mozo": "Menu editor for MATE using the freedesktop.org menu specification",
	"pluma": "A powerful text editor for MATE",
	"mate-calc": "Calculator for MATE",
	"mate-notification-daemon": "Daemon to display passive pop-up notifications",
	"mate-applets": "Applets for use with the MATE panel"
}

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
		package['description'] = mate_descriptions[name]
		package['section'] = mate_sections[name]
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

