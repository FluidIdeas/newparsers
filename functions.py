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

def get_tarball(download_urls):
	if len(download_urls) > 0:
		return download_urls[0].split('/')[-1]

def is_number(number):
	for ch in number:
		if not str(ch).isdigit() and ch != '.':
			return False
	return True

def get_version(tarball):
	if tarball != None and is_number(tarball):
		return tarball
	start = -1
	end = -1
	if tarball != None:
		#print(tarball)
		for i, ch in enumerate(tarball):
			#print(str(i) + ': ' + str(ch))
			if (str(ch).isdigit() and tarball[i + 1] != '-' or ch == '.') and start == -1:
				#print('Start initialized')
				start = i
			if str(ch).isdigit() == False and start != -1 and ch != '.':
				#print('End initialized')
				end = i - 1
				break
		#print(str(start) + ':' + str(end))
		return tarball[start:end]

def process_html_data(data):
	parts = data.split(' ')
	space_removed = ''
	for part in parts:
		if part == '':
			continue
		space_removed = space_removed + part
		if not part[-1] == '\n':
			space_removed = space_removed + ' '
	modified = space_removed.replace('=\n', '=')
	print(modified)
	return modified

def parse_package(file_path):
	package = dict()
	doc = BeautifulSoup(read_raw(file_path).decode("latin-1"), 'html.parser')
	package['name'] = file_path.split('/')[-1].replace('.html', '')
	package['download_urls'] = list()
	package['dependencies'] = list()
	download_links = doc.select('div.itemizedlist ul.compact a.ulink[href]')
	for link in download_links:
		package['download_urls'].append(link.attrs['href'])
	for link in doc.select('p.required a.xref , p.recommended a.xref '):
		package['dependencies'].append(link.attrs['href'].split('/')[-1].replace('.html', ''))
	package['tarball'] = get_tarball(package['download_urls'])
	package['version'] = get_version(package['tarball'])
	commands = list()
	cmd_pres = doc.select('pre.userinput, pre.root')
	for cmd_pre in cmd_pres:
		if cmd_pre.attrs['class'][0] == 'userinput':
			commands.append(cmd_pre.select('kbd.command')[0].text.strip())
		elif cmd_pre.attrs['class'][0] == 'root':
			if len(cmd_pre.select('kbd.command')) == 0:
				continue
			else:
				cmd = cmd_pre.select('kbd.command')[0].text.strip()
			root_cmd = 'cat > /tmp/root_script.sh <<"ENDOFSCRIPT"\n' + cmd + '\nENDOFSCRIPT\n\nchmod a+x /tmp/root_script.sh\n/tmp/root_script.sh\n'
			commands.append(root_cmd)
		package['commands'] = '\n'.join(commands)
	return package

def print_package(package):
	print(package['name'])
	print(package['download_urls'])
	print(package['dependencies'])
	print(package['tarball'])
	print(package['version'])
	print(package['commands'])

