#!/usr/bin/python3
import sys
import os
import itertools
os.chdir(os.path.dirname(__file__))
sys.path.append('..')
import libcompiler as libcompiler
from libcompiler import (
		set_font, set_npress_array, get_disassembly, get_commands,
		read_rename_list, set_symbolrepr, get_rom,
		optimize_gadget, find_equivalent_addresses,
		to_font, print_addresses,
		process_program
		)
#get_rom('rom.bin')
get_rom('rom.bin')
get_disassembly('disas.txt')
get_commands('gadgets')
read_rename_list('labels')
read_rename_list('../labels_sfr')

FONT=[l.split('\t') for l in '''
															
𝒙	𝒚	𝒛	⋯	▲	▼	▸	 ˍ	$	◁	&	𝑡	ᴛ	ₜ	ₕ	₅
 	!	"	#	×	%	÷	'	(	)	⋅	+	,	—	.	/
0	1	2	3	4	5	6	7	8	9	:	;	<	=	>	?
@	A	B	C	D	E	F	G	H	I	J	K	L	M	N	O
P	Q	R	S	T	U	V	W	X	Y	Z	[	▫	]	^	_
-	a	b	c	d	e	f	g	h	i	j	k	l	m	n	o
p	q	r	s	t	u	v	w	x	y	z	{	|	}	~	⊢
𝐢	𝐞	x	⏨	∞	°	ʳ	ᵍ	∠	x̅	y̅	x̂	ŷ	→	∏	⇒
ₓ	⏨	⏨̄	⌟	≤	≠	≥	⇩	√	∫	ᴀ	ʙ	ᴄ	ₙ	▶	◀	
⁰	¹	²	³	⁴	⁵	⁶	⁷	⁸	⁹	⁻¹	ˣ	¹⁰	₍	₎	±	
₀	₁	₂	₋₁	ꜰ	ɴ	ᴘ	µ	𝐀	𝐁	𝐂	𝐃	𝐄	𝐅	𝐏	▷	
Σ	α	γ	ε	θ	λ	μ	π	σ	ϕ	ℓ	ℏ	█	⎕	₃	▂
𝐟	𝐩	𝐧	𝛍	𝐦	𝐤	𝐌	𝐆	𝐓	𝐏	𝐄	𝑭	ₚ	ₑ	ᴊ	ᴋ
τ	ᵤ	₉	Å	ₘ	ɪ	₄									
															
'''.strip('\n').split('\n')]
assert len(FONT)==16 # TODO wrong
assert all(len(l)>=16 for l in FONT)
FONT=[*itertools.chain.from_iterable(l[:16] for l in FONT)]

set_font(FONT)

npress=( # 99: nul, 49: not typeable, 24: can be extracted from multibyte characters
		# 30: box
	99,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,
	24,24,24,24,24,24,24,24,24,30,24,24,24,24,24,24,
	24,2 ,2 ,2 ,24,24,24,24,24,24,24,24,2 ,1 ,1 ,24,
	1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,24,24,24,24,24,24,
	2 ,1 ,2 ,2 ,2 ,2 ,2 ,2 ,1 ,2 ,2 ,2 ,24,24,24,24,
	2 ,1 ,2 ,2 ,24,24,24,24,24,24,24,24,24,24,24,49,
	1 ,49,49,49,49,49,49,49,2 ,2 ,49,49,3 ,3 ,3 ,3 ,
	3 ,3 ,2 ,2 ,1 ,1 ,2 ,1 ,1 ,1 ,2 ,2 ,2 ,1 ,2 ,2 ,
	49,49,49,2 ,2 ,49,49,2 ,2 ,2 ,49,49,49,49,49,49,
	49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,
	49,49,49,49,49,2 ,1 ,1 ,1 ,1 ,2 ,49,49,2 ,2 ,49,
	49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,
	1 ,49,49,49,49,49,49,49,1 ,1 ,2 ,49,49,49,49,49,
	1 ,49,49,49,1 ,1 ,2 ,2 ,2 ,3 ,3 ,3 ,1 ,3 ,3 ,3 ,
	3 ,3 ,3 ,3 ,3 ,3 ,3 ,3 ,49,49,49,49,49,49,49,49,
	49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49, # TODO fix npress table for multibyte characters
	)
set_npress_array(npress)

def get_binary(filename):
	file = open(filename, 'rb')
	result = file.read()
	file.close()
	return result

from get_char_table import f as get_symbol
symbols = [
		''.join(map(FONT.__getitem__,get_symbol(x)[1]))
			for x in range(0xf0)] + \
	['@']*0x10 # TODO wrong




set_symbolrepr(symbols[:])

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--target', default='none',
		choices=('none',),
		help='how will the output be used')
parser.add_argument('-f', '--format', default='key',
		choices=('hex', 'key'),
		help='output format')
parser.add_argument('-g', '--gadget-adr', default=None,
		type=lambda x:int(x,0), help='Address of gadget to optimize')
parser.add_argument('-gb', '--gadget-bin', default=None, help='Gadget in binary (big endian)')
parser.add_argument('-gn', '--gadget-nword', default=0,
		type=lambda x:int(x,0), help='Length of gadget to optimize (inf if not provided)')
parser.add_argument('-p', '--preview-count', default=0,
		type=lambda x:int(x,0), help='Number of lines to preview (optimize gadget mode)')
args = parser.parse_args()

if args.gadget_bin is not None:
	assert args.gadget_bin
	print_addresses(optimize_gadget(bytes.fromhex(args.gadget_bin)), args.preview_count)

elif args.gadget_nword>0:
	print_addresses(
		optimize_gadget(libcompiler.rom[args.gadget_adr:args.gadget_adr+args.gadget_nword*2]),
		args.preview_count)

elif args.gadget_adr is not None:
	print_addresses(
		find_equivalent_addresses(libcompiler.rom,{args.gadget_adr}),
		args.preview_count)

else:
	program = sys.stdin.read().split('\n')
	process_program(args, program, overflow_initial_sp=0xE9E0)
