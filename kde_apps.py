#!/usr/bin/env python3

import subprocess
from bs4 import BeautifulSoup
from decimal import Decimal

inclusions = ['kcalc', 'dolphin', 'dolphin-plugins', 'kate', 'kget']

def apps_url(version):
    url = "https://download.kde.org/stable/applications/" + version + "/src/"
    return url

def download(version):
    proc = subprocess.Popen('wget ' + apps_url(version) + ' -O /tmp/kde_apps &> /dev/null', shell=True)
    proc.communicate()
    proc.wait()

def collect_anchors(version):
    download(version)
    a_list = list()
    with open('/tmp/kde_apps') as fp:
        doc = BeautifulSoup(fp.read(), features="lxml")
        anchors = doc.select('a')
        for anchor in anchors:
            a_list.append(anchor)
    return a_list

def get_version(tarball):
    s = tarball[tarball.rindex('-') + 1: tarball.rindex('.tar.xz')]
    return s.split('.')

def get_tarball(anchor):
    return anchor.attrs['href']

def get_url(apps_url, anchor):
    return apps_url + get_tarball(anchor)

def get_name(anchor):
    tarball = get_tarball(anchor)
    return tarball[: tarball.rindex('-')]

def get_packages(version, plasma_all, frameworks):
    anchors = collect_anchors(version)
    packages = list()
    for anchor in anchors:
        url = get_url(apps_url(version), anchor)
        tarball = get_tarball(anchor)
        if url.endswith('.tar.xz'):
            if get_name(anchor) not in inclusions:
                continue
                
            packages.append({
                'name': get_name(anchor),
                'version': '.'.join(get_version(tarball)),
                'tarball': tarball,
                'download_urls': [
                    url
                ],
                'commands': 'mkdir build\ncd build\n\ncmake -DCMAKE_INSTALL_PREFIX=/usr ..\nmake -j$(nproc)\n\nsudo make install',
                'dependencies': []
            })
    return packages
