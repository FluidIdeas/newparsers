#!/usr/bin/env python3

import subprocess
from bs4 import BeautifulSoup
from decimal import Decimal

inclusions = ['kcalc', 'dolphin', 'dolphin-plugins', 'kate', 'kget']

descriptions = {
    "kcalc": "DescriptionKCalc is the software calculator integrated with the KDE Software Compilation. In the default view it includes a number pad, buttons for adding, subtracting, multiplying, and dividing, brackets, memory keys, percent, reciprocal, factorial, square, square root, and x to the power of y buttons.",
    "dolphin": "Dolphin is a free and open source file manager included in the KDE Applications bundle. Dolphin became the default file manager of KDE Plasma desktop environments in the fourth iteration, termed KDE Software Compilation 4. It can also be optionally installed on K Desktop Environment 3.",
    "dolphin-plugins": "These plugins integrate Dolphin with the revision control systems Bazaar, Mercurial and Git. A Dropbox plugin gives action items to keep your files synced to the Dropbox service.",
    "kate": "DescriptionThe KDE Advanced Text Editor is a text editor developed by the KDE free software community. It has been a part of KDE Software Compilation since version 2.2, which was first released in 2001.",
    "kget": "KGet is a versatile and user-friendly download manager."
}
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
                'description': descriptions[get_name(anchor)],
                'section': 'KDE Frameworks 5 Based Applications',
                'version': '.'.join(get_version(tarball)),
                'tarball': tarball,
                'download_urls': [
                    url
                ],
                'commands': 'mkdir build\ncd build\n\ncmake -DCMAKE_INSTALL_PREFIX=/usr ..\nmake -j$(nproc)\n\nsudo make install',
                'dependencies': []
            })
    return packages
