#!/usr/bin/env python3

from bs4 import BeautifulSoup

def read_processed(file_path):
	with open(file_path, 'rb') as fp:
		data = fp.read()
	return data

def read_raw(file_path):
	with open(file_path, 'rb') as fp:
		data = fp.read()
	return data

def parse_package(file_path):
	package = dict()
	doc = BeautifulSoup(read_raw(file_path), 'html.parser')
	package['name'] = file_path.split('/')[-1].replace('.html', '')
	package['download_urls'] = list()
	package['dependencies'] = list()
	download_links = doc.select('div.itemizedlist ul.compact a.ulink[href]')
	for link in download_links:
		package['download_urls'].append(link.attrs['href'])
	for link in doc.select('p.required a.xref , p.recommended a.xref '):
		package['dependencies'].append(link.attrs['href'].split('/')[-1].replace('.html', ''))
	return package
