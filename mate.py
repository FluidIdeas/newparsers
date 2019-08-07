#!/usr/bin/env python3

import subprocess
from bs4 import BeautifulSoup
from decimal import Decimal

mate_base_url='https://pub.mate-desktop.org/releases/'
p = subprocess.Popen('wget ' + mate_base_url + ' -O /tmp/index.html', shell=True)
p.communicate()
p.wait()

with open('/tmp/index.html') as fp:
	doc = BeautifulSoup(fp.read(), features='lxml')

anchors = doc.select('a[href]')

versions = list()

for anchor in anchors:
	if anchor.attrs['href'] != '../' and anchor.attrs['href'] != 'themes/':
		v = anchor.text.replace('/', '')
		versions[float(v)] = v
print(versions)
