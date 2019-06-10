#!/usr/bin/env python3

from bs4 import BeautifulSoup
from functions import read_processed
from functions import read_raw

index = 1
separator = '/'
book_dir = '/home/chandrakant/aryalinux/books/lfs'
scripts_dir = '/home/chandrakant/aryalinux/aryalinux/base-system'
index_path = book_dir + separator + 'index.html'
wget_list_path = book_dir + separator + 'wget-list'
chapter_map = {'chapter05': 'toolchain', 'chapter06': 'final-system'}
unwanted_chapters = ['5.1', '5.2', '5.3', '5.36', '5.37', '6.1', '6.2', '6.3', '6.4', '6.5', '6.6', '6.77', '6.78', '6.79']

additional_commands = {
	'openssl': 'ln -svf /tools/bin/env /usr/bin/'
}
deletables = [
	"vim -c ':options'",
	'make check',
	'make -k check',
	'bash tests/run.sh',
	'make PERL5LIB=$PWD/tests/ check',
	'make NON_ROOT_USERNAME=nobody check-root',
	'echo "dummy:x:1000:nobody" >> /etc/group',
	'chown -Rv nobody .',
	'RUN_EXPENSIVE_TESTS=yes',
	"sed -i '/dummy/d' /etc/group",
	'make test',
	'make -j4 check',
	'make -k test',
	'make -j1 check',
	'make tests',
	'ulimit -s 32768',
	'rm ../gcc/testsuite/g++.dg/pr83239.C',
	'../contrib/test_summary',
	'gmp-check-log',
	'expect -c "spawn ls"',
	'Test/checklib.b',
	'mkdir -pv /usr/lib/locale',
	'./ninja ninja_test',
	'exec /bin/bash --login +h',
	'ABI=32 ./configure',
	'tzselect',
	'passwd root',
	'vim-test.log'
]

replaceables = {
	'<paper_size>': '$PAPER_SIZE',
	'en_US.UTF-8': '$LOCALE',
	'/usr/share/zoneinfo/<xxx>': '/usr/share/zoneinfo/$TIMEZONE'
}

fixed_scripts = {
	'grub': 'scripts/grub.sh'
}

tarballs = list()

with open(wget_list_path, 'r') as fp:
	downloads = fp.read().split('\n')
for download in downloads:
	tarballs.append(download.split('/')[-1])

package_tarballs = dict()


for tarball in tarballs:
	if 'linux-5' in tarball:
		package_tarballs['linux-headers'] = tarball
	elif 'tar' in tarball and tarball.index('tar') == 0:
		package_tarballs['tar'] = tarball
	elif 'binutils' in tarball:
		package_tarballs['binutils-pass1'] = tarball
		package_tarballs['binutils-pass2'] = tarball
	elif 'gcc' in tarball and tarball.index('gcc') == 0:
		package_tarballs['gcc-pass1'] = tarball
		package_tarballs['gcc-pass2'] = tarball
		package_tarballs['gcc-libstdc++'] = tarball
	elif 'XML-Parser' in tarball:
		package_tarballs['xml-parser'] = tarball
	elif 'elfutils' in tarball:
		package_tarballs['libelf'] = tarball
	elif 'make' in tarball and tarball.index('make') == 0:
		package_tarballs['make'] = tarball
	elif 'xz' in tarball and tarball.index('xz') == 0:
		package_tarballs['xz'] = tarball

def get_prefix(i):
	if i < 10:
		return '00' + str(i)
	elif i < 100:
		return '0' + str(i)
	else:
		return str(i)

def clean_commands(commands):
	fresh_commands = list()
	for command in commands:
		replaceable = command
		for deletable in deletables:
			if deletable in command:
				if deletable in command:
					replaceable = None
				else:
					replaceable = command.replace(deletable, '')
		for s, v in replaceables.items():
			if replaceable != None and s in replaceable:
				replaceable = replaceable.replace(s, v)
		if replaceable != None:
			fresh_commands.append(replaceable)
	return fresh_commands

def get_commands(document, name):
	commands = document.select('kbd.command')
	cmds = list()
	for command in commands:
		cmds.append(command.text.strip())
	cleaned = clean_commands(cmds)
	if name in additional_commands:
		cleaned.insert(0, additional_commands[name])
	return cleaned

def get_tarball_name(name):
	if name in package_tarballs:
		return package_tarballs[name]
	else:
		for tarball in tarballs:
			if name in tarball:
				return tarball

def get_script(package):
	output = list()
	output.append('#!/bin/bash')
	output.append('')
	output.append('set -e')
	output.append('set +h')
	output.append('')
	output.append('. /sources/build-properties')
	output.append('. /sources/build-functions')
	output.append('')
	output.append('NAME=' + package['script_name'])
	output.append('')
	output.append('touch /sources/build-log')
	output.append('if ! grep "$NAME" /sources/build-log; then')
	output.append('')
	output.append('cd /sources')
	output.append('')
	if package['tarball'] != None:
		output.append('TARBALL=' + package['tarball'])
		output.append('DIRECTORY=$(tar tf $TARBALL | cut -d/ -f1 | uniq)')
		output.append('')
		output.append('tar xf $TARBALL')
		output.append('cd $DIRECTORY')
		output.append('')
	output.append('''export CFLAGS="-march=$BUILD_ARCH -mtune=$BUILD_TUNE -O$BUILD_OPT_LEVEL"
export CXXFLAGS="-march=$BUILD_ARCH -mtune=$BUILD_TUNE -O$BUILD_OPT_LEVEL"
export CPPFLAGS="-march=$BUILD_ARCH -mtune=$BUILD_TUNE -O$BUILD_OPT_LEVEL"''')
	output.append('')
	output.append('\n'.join(package['commands']))
	output.append('')
	output.append('fi')
	output.append('')
	output.append('cleanup $DIRECTORY')
	output.append('log $NAME')
	return output

index_data = read_processed(index_path)
document = BeautifulSoup(index_data, features='lxml')
links = document.select('li.sect1 a[href]')

chapters_links = dict()

for link in links:
	href = link.attrs['href']
	if '/' in href:
		chapter = href[:href.index('/')]
		if chapter in chapter_map.keys():
			if chapter_map[chapter] not in chapters_links:
				chapters_links[chapter_map[chapter]] = list()
			chapters_links[chapter_map[chapter]].append(book_dir + separator + href)

packages = list()
for chapter, links in chapters_links.items():
	for link in links:
		data = read_raw(link)
		document = BeautifulSoup(data, 'html.parser')
		title = document.select('html head title')[0].text.strip()
		chapter = title.split()[0][0:-1]
		title = ' '.join(title.split()[1:])
		if chapter in unwanted_chapters:
			continue
		package = dict()
		package['name'] = link.split('/')[-1].replace('.html', '')
		package['commands'] = get_commands(document, package['name'])
		package['tarball'] = get_tarball_name(package['name'])
		if chapter[0] == '5':
			package['dir'] = 'toolchain'
		elif chapter[0] == '6':
			package['dir'] = 'final-system'
		prefix = get_prefix(index)
		package['script_name'] = prefix + '-' + package['name'].lower()
		packages.append(package)
		index = index + 1

for package in packages:
	if package['name'] in fixed_scripts:
		with open(fixed_scripts[package['name']], 'r') as fp:
			with open(scripts_dir + separator + package['dir'] + separator + package['script_name'] + '.sh', 'w') as fpout:
				fpout.write(fp.read())
	else:
		output = '\n'.join(get_script(package))
		with open(scripts_dir + separator + package['dir'] + separator + package['script_name'] + '.sh', 'w') as fpout:
			fpout.write(output)

with open(wget_list_path, 'r') as fpin:
	with open(scripts_dir + separator + 'wget-list', 'w') as fpout:
		fpout.write(fpin.read())

