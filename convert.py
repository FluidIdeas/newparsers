#!/usr/bin/env python3

import json
from functions import get_tarball
from functions import load_json

command_deletion_list = load_json('config/command_deletion_list.json')

deletion_dict = dict()
for command_deletion in command_deletion_list:
	for key, value in command_deletion.items():
		deletion_dict[key] = value

with open('config/deletion.json', 'w') as fp:
	fp.write(json.dumps(deletion_dict, indent=4, separators=(',', ': ')))

