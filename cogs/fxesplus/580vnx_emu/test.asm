org 0xd730
render:
    render.ddd4
setup_key:
    getkeycode
    setlr
    ea = adr_of normal_table
    call 09c20
    qr0=[ea],lea D002H,[ea]=qr0
    er4 = adr_of gadget
    [er4]=er0,pop er0,rt
pos:
    0x0000
gadget:
    nop
setup_move_key:
    er2 = 0xd150
    er0 = [er2],r2 = 9,rt
    ea = adr_of move_table
    call 09c20
    qr0=[ea],lea D002H,[ea]=qr0
    er2 = er0,er0 = er2,pop er8,rt
    adr_of [+4784] pos
    [er8]+=er2,pop xr8
    0xd182
    0xd182
loop:
    xr0 = hex 30 d6 84 d1
    BL strcpy
    hex 72 1f
normal_table:
    hex 32 00
    0x91e6
    hex 31 00
    0x91ea
    hex 26 fc
    0x8c60
    hex 00 00
    0xeaaa
move_table:
    hex 40 04
    0xffff
    hex 80 08
    0x0001
    hex 80 04
    0xff00
    hex 40 08
    0x0100
    hex 00 00
    0x0000