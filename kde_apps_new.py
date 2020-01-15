#!/usr/bin/env python3

import sys
import requests
import json
from bs4 import BeautifulSoup

frameworks_version_url="https://download.kde.org/stable/frameworks"
packages = [
	'extra-cmake-modules',
	'kwindowsystem'
]

prefixes = {
	'extra-cmake-modules': "sed -i '/\"lib64\"/s/64//' kde-modules/KDEInstallDirs.cmake"
}

suffixes = {
}

def debug(msg):
	if debug_mode:
		print(msg)

def get_latest_framework_version():
	response = requests.get(frameworks_version_url)
	if response.status_code == 200:
		doc = BeautifulSoup(response.content, 'lxml')
	anchors = doc.select('a')
	selected_anchors = list()
	for anchor in anchors:
		if anchor.text == anchor.attrs['href']:
			selected_anchors.append(anchor)
	versions = list()
	for a in selected_anchors:
		versions.append(a.attrs['href'])
	majors = dict()
	for version in versions:
		parts = version.split('.')
		if parts[0] not in majors:
			majors[parts[0]] = list()
		majors[parts[0]].append(parts[1][:-1])
	all_majors = list(majors.keys())
	all_majors.sort()
	selected_major = all_majors[len(all_majors) - 1]
	all_minors = list()
	for minor in majors[selected_major]:
		all_minors.append(minor)
	all_minors.sort()
	return selected_major + '.' + all_minors[len(all_minors) - 1]

def get_latest_urls_for_selected():
	latest_version = get_latest_framework_version()
	frameworks_url = frameworks_version_url + '/' + latest_version
	response = requests.get(frameworks_url)
	if response.status_code == 200:
		doc = BeautifulSoup(response.content, 'lxml')
		select_anchors = list()
		all_anchors = doc.select('a')
		for anchor in all_anchors:
			if anchor.attrs['href'] == anchor.text and 'tar.xz.sig' not in anchor.text and '.zip' not in anchor.text:
				select_anchors.append(anchor)
		filtered_anchors = list()
		for anchor in select_anchors:
			for package in packages:
				if package in anchor.text and anchor.text.index(package) == 0:
					filtered_anchors.append(anchor)
		urls = list()
		for anchor in filtered_anchors:
			urls.append(frameworks_url + '/' + anchor.attrs['href'])
		return urls

def get_tarball(url):
	return url[url.rindex('/') + 1:]

def get_version(url):
	tarball = get_tarball(url)
	version = tarball[tarball.rindex('-') + 1:tarball.rindex('.tar.xz')]
	return version

def get_name(url):
	tarball = get_tarball(url)
	version = get_version(url)
	return tarball.replace('-' + version + '.tar.xz', '')

def create_data():
	data = dict()
	data['name'] = None
	data['version'] = None
	data['download_urls'] = list()
	data['url'] = None
	data['tarball'] = None
	data['commands'] = None
	data['dependencies'] = list()
	return data

def get_data(debug_mode):
	latest_urls = get_latest_urls_for_selected()
	all_data = list()
	for url in latest_urls:
		data = create_data()
		data['download_urls'].append(url)
		data['name'] = get_name(url)
		data['version'] = get_version(url)
		data['tarball'] = get_tarball(url)
		data['commands'] = 'mkdir build\ncd build\n\ncmake -DCMAKE_INSTALL_PREFIX=/usr \\\n-DCMAKE_BUILD_TYPE=Release \\\n-DBUILD_TESTING=OFF \\\n-Wno-dev .. &&\nmake -j$(nproc)\nsudo make install'
		if data['name'] in prefixes:
			data['commands'] = prefixes[data['name']] + '\n\n' + data['commands']
		all_data.append(data)
	return all_data

