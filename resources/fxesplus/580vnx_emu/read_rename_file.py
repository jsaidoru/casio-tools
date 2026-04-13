def read_rename_list(filename):
	'''Try to parse a rename list.

	If the rename list is ambiguous without disassembly, it raises an error.
	'''
	global commands, datalabels
	with open(filename, 'r', encoding='u8') as f:
		data = f.read().splitlines()

	line_regex   = re.compile(r'^\s*([\w_.]+)\s+([\w_.]+)')
	global_regex = re.compile(r'f_([0-9a-fA-F]+)')
	local_regex  = re.compile(r'.l_([0-9a-fA-F]+)')
	data_regex   = re.compile(r'd_([0-9a-fA-F]+)')
	hexadecimal  = re.compile(r'[0-9a-fA-F]+')

	last_global_label = None
	for line_index0, line in enumerate(data):
		match = line_regex.match(line)
		if not match: 
			continue
		raw, real = match[1], match[2]
		if real.startswith('.'):
			# we don't get local labels.
			continue

		match = data_regex.fullmatch(raw)
		if match:
			addr = int(match[1], 16)
			datalabels[real] = addr
			continue

		addr = None
		if hexadecimal.fullmatch(raw):
			addr = int(raw, 16)
			last_global_label = None
			# because we don't know whether this label is global or local
		else:
			match = global_regex.match(raw)
			if match:
				addr = int(match[1], 16)
				if len(match[0]) == len(raw):  # global_regex.fullmatch
					last_global_label = addr
				else:
					match = local_regex.fullmatch(raw[len(match[0]):])
					if match:  # full address f_12345.l_67
						addr += int(match[1], 16)
			else:
				match = local_regex.fullmatch(raw)
				if match:
					if last_global_label is None:
						print('Label cannot be read: ', line)
						continue
					else:
						addr = last_global_label + int(match[1], 16)

		if addr is not None:
			assert addr < len(disasm), f'{addr:05X}'
			if disasm[addr].startswith('push lr'):
				tags = 'del lr',
				addr += 2
			else:
				tags = 'rt',
				a1 = addr + 2
				while not any(disasm[a1].startswith(x) for x in ('push lr', 'pop pc', 'rt')): 
					a1 += 2
				if not disasm[a1].startswith('rt'):
					tags = tags + ('del lr',)

			if real in commands:
				if 'override rename list' in commands[real][1]:
					continue
				if commands[real] == (addr, tags):
					note(f'Warning: Duplicated command {real}\n')
					continue

			add_command(commands, addr, real, tags=tags,
					debug_info=f'at {filename}:{line_index0+1}')
		else:
			raise ValueError('Invalid line: ' + repr(line))