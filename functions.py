#!/usr/bin/env python3

from bs4 import BeautifulSoup
import json

systemd_service_tarball_url = 'http://www.linuxfromscratch.org/blfs/downloads/systemd/blfs-systemd-units-20180105.tar.bz2'
systemd_service_tarball = systemd_service_tarball_url.split('/')[-1]
systemd_service_dir = systemd_service_tarball[0:systemd_service_tarball.index('.')]

with open('config/templates/script_template') as tfp:
	template = tfp.read()

def load_json(file_path):
	with open(file_path, 'r') as fp:
		return json.load(fp)

deletions = load_json('config/deletion.json')
variables = load_json('config/variables.json')
expendable_deps = load_json('config/expendable_dependencies.json')
replaceable_deps = load_json('config/replacable_dependencies.json')
pkg_expendable_deps = load_json('config/package_expendable_dependencies.json')
url_deletion = load_json('config/url_deletion.json')
replaceable_cmds = load_json('config/replaceable_commands.json')

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
				if '-' in tarball and i < tarball.index('-'):
					continue
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

def get_systemd_service_install_cmds(cmd):
	return '#!/bin/bash\n\nset -e\nset +h\n\n. /etc/alps/alps.conf\n\npushd $SOURCE_DIR\nwget -nc ' + systemd_service_tarball_url + '\ntar xf ' + systemd_service_tarball + '\ncd ' + systemd_service_dir + '\nsudo ' + cmd + '\npopd'

def Diff(li1, li2):
	result = li1.copy()
	for item in li2:
		if item in result:
			result.remove(item)
	return result

def clean_dependencies(package):
	new_deps = list()
	for dep in package['dependencies']:
		if 'x7driver#' in dep and dep.index('x7driver#') == 0:
			new_deps.append(dep.replace('x7driver#', ''))
			continue
		if dep not in expendable_deps:
			new_deps.append(dep.lower())
	final_deps = list()
	for dep in new_deps:
		if '/' in dep:
			final_deps.append(dep[dep.rindex('/') + 1:])
		else:
			final_deps.append(dep)
	if package['name'] in pkg_expendable_deps:
		package['dependencies'] = Diff(final_deps, pkg_expendable_deps[package['name']])
	else:
		package['dependencies'] = final_deps
	for dep, replacement in replaceable_deps.items():
		if dep in package['dependencies']:
			package['dependencies'].remove(dep)
			package['dependencies'].append(replacement)

def delete_url_if_needed(package):
	if package['name'] in url_deletion:
		package['download_urls'].clear()

def clean_commands(package):
	for key, value in replaceable_cmds.items():
		if 'commands' in package and key in package['commands']:
			package['commands'] = package['commands'].replace(key, value)

def parse_package(file_path):
	package = dict()
	doc = BeautifulSoup(read_raw(file_path).decode("latin-1"), 'html.parser')
	package['name'] = file_path.split('/')[-1].replace('.html', '').lower()
	package['download_urls'] = list()
	package['dependencies'] = list()
	download_links = doc.select('div.itemizedlist ul.compact a.ulink[href]')
	for link in download_links:
		package['download_urls'].append(link.attrs['href'])
	for link in doc.select('p.required a.xref , p.recommended a.xref '):
		package['dependencies'].append(link.attrs['href'].split('/')[-1].replace('.html', ''))
	clean_dependencies(package)
	package['tarball'] = get_tarball(package['download_urls'])
	package['version'] = get_version(package['tarball'])
	commands = list()
	cmd_pres = doc.select('pre.userinput, pre.root')
	for cmd_pre in cmd_pres:
		if package['name'] == 'sudo':
			commands.append(cmd_pre.select('kbd.command')[0].text.strip())
		else:
			if cmd_pre.attrs['class'][0] == 'userinput':
				commands.append(cmd_pre.select('kbd.command')[0].text.strip())
			elif cmd_pre.attrs['class'][0] == 'root':
				if len(cmd_pre.select('kbd.command')) == 0:
					continue
				else:
					cmd = cmd_pre.select('kbd.command')[0].text.strip()
					if 'make install-' in cmd and cmd.index('make install-') == 0:
						cmd = get_systemd_service_install_cmds(cmd)
				root_cmd = 'sudo rm -rf /tmp/rootscript.sh\ncat > /tmp/rootscript.sh <<"ENDOFROOTSCRIPT"\n' + cmd + '\nENDOFROOTSCRIPT\n\nchmod a+x /tmp/rootscript.sh\nsudo /tmp/rootscript.sh\nsudo rm -rf /tmp/rootscript.sh\n'
				commands.append(root_cmd)
		cmds = list()
		if package['name'] in deletions:
			for command in commands:
				do_add = True
				for deletable in deletions[package['name']]:
					if deletable in command:
						do_add = False
						break
				if do_add:
					cmds.append(command)
		else:
			cmds = commands

		package['commands'] = '\n'.join(cmds)
		str_vars = ''
		for key, value in variables.items():
			if key in package['commands']:
				str_vars = str_vars + key + '="' + value + '"\n'
		package['commands'] = str_vars + '\n' + package['commands']
	delete_url_if_needed(package)
	clean_commands(package)
	return package

def parse_perl_modules(file_path):
	modules = list()
	doc = BeautifulSoup(read_raw(file_path).decode("latin-1"), 'html.parser')
	module_links = doc.select('div.itemizedlist ul.compact li p a.xref')
	for module_link in module_links:
		package = dict()
		name = module_link.attrs['href'][module_link.attrs['href'].index('#') + 1:]
		prefix = module_link.attrs['href'][:module_link.attrs['href'].index('#')].replace('.html', '')
		if prefix == 'x7driver':
			prefix = ''
		if 'perl-alternative' in name:
			continue
		if prefix != '':
			package['name'] = prefix + '#' + name
		else:
			package['name'] = name
		package['name'] = package['name'].lower()
		module_div = doc.select('div.sect2 h2.sect2 a#' + name)[0].parent.parent.select('div.package, div.installation')
		package['download_urls'] = list()
		urls = module_div[0].select('ul.compact  li p a.ulink')
		for url in urls:
			package['download_urls'].append(url.attrs['href'])
		package['url'] = package['download_urls'][0]
		package['dependencies'] = list()
		deps = module_div[0].select('p.recommended a.xref, p.required a.xref')
		for dep in deps:
			package['dependencies'].append(dep.attrs['href'].replace('.html', ''))
		clean_dependencies(package)
		commands = list()
		cmds = module_div[1].select('pre.userinput, pre.root')
		for cmd in cmds:
			if cmd.attrs['class'][0] == 'userinput':
				commands.append(cmd.select('kbd.command')[0].text.replace('&&\nmake test', '').strip())
			elif cmd.attrs['class'][0] == 'root':
				commands.append('sudo rm -rf /tmp/rootscript.sh\ncat > /tmp/rootscript.sh <<"ENDOFROOTSCRIPT"\n' + cmd.select('kbd.command')[0].text + '\nENDOFROOTSCRIPT\n\nchmod a+x /tmp/rootscript.sh\nsudo /tmp/rootscript.sh\nsudo rm -rf /tmp/rootscript.sh\n')
		cmds = list()
		if package['name'] in deletions:
			for command in commands:
				do_add = True
				for deletable in deletions[package['name']]:
					if deletable in command:
						do_add = False
						break
				if do_add:
					cmds.append(command)
		else:
			cmds = commands
		package['commands'] = '\n'.join(cmds)
		package['tarball'] = get_tarball(package['download_urls'])
		package['version'] = get_version(package['tarball'])
		clean_commands(package)
		str_vars = ''
		for key, value in variables.items():
			if key in package['commands']:
				str_vars = str_vars + key + '="' + value + '"\n'
		package['commands'] = str_vars + '\n' + package['commands']
		modules.append(package)
	return modules

def print_package(package):
	print(package['name'])
	print(package['download_urls'])
	print(package['dependencies'])
	print(package['tarball'])
	print(package['version'])
	print(package['commands'])

def get_script(p):
	tmp = '' + template
	deps = ''
	if p['dependencies'] != None:
		for dep in p['dependencies']:
			deps = deps + '#REQ:' + dep + '\n'
	else:
		deps = ''
	tmp = tmp.replace('##DEPS##', deps)
	if p['name'] != None:
		tmp = tmp.replace('##NAME##', 'NAME=' + p['name'])
	if p['version'] != None:
		tmp = tmp.replace('##VERSION##', 'VERSION=' + p['version'])
	else:
		tmp = tmp.replace('##VERSION##', '')
	urls = ''
	if len(p['download_urls']) > 0:
		tmp = tmp.replace('##URL##', 'URL=' + p['download_urls'][0])
		for url in p['download_urls']:
			urls = urls + 'wget -nc ' + url + '\n'
		tmp = tmp.replace('##DOWNLOADS##', urls)
	else:
		tmp = tmp.replace('##URL##', '')
		tmp = tmp.replace('##DOWNLOADS##', '')
		tmp = tmp.replace('##VERSION##', '')
	if p['commands'] == None or len(p['commands']) > 0:
		tmp = tmp.replace('##COMMANDS##', p['commands'])
	else:
		tmp = tmp.replace('##COMMANDS##', '')
	return tmp

def package_clone(package, new_name, removable_deps):
	pkg = package.copy()
	pkg['name'] = new_name
	for dep in removable_deps:
		if dep in pkg['dependencies']:
			pkg['dependencies'].remove(dep)
	return pkg

def find_package(packages, name):
	for package in packages:
		if package['name'] == name:
			return package

