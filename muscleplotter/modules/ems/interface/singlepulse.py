#!/usr/bin/python
# Filename: singlepulse.py

import binascii
import struct

safety_limit = 30

version = '0.1'

get_bin = lambda x, n: x >= 0 and str(bin(x))[2:].zfill(n) or "-" + str(bin(x))[3:].zfill(n)

#type of command
CHANNEL_INIT = 0
CHANNEL_UPDATE = 1
CHANNEL_STOP = 2
SINGLE_PULSE = 3

def generate(_channel_number,_pulse_width,_pulse_current):
	global safety_limit
	ident = SINGLE_PULSE
	channel_number = _channel_number-1
	pulse_width = _pulse_width
	if (_pulse_current < safety_limit):
		pulse_current = _pulse_current
	else:
		print("SAFETY LIMIT (of " + str(safety_limit) + " EXCEEDED. Request of " + str(_pulse_current) + "dropped to limit")
		pulse_current = safety_limit  
	checksum = (channel_number + pulse_width + pulse_current) % 32
	#print("checksum verify = " + str(checksum))

	#print("binary command: \n" + 
	#"\t" + get_bin(ident,2) +  "\t\t#ident\t\t"+ str(len(get_bin(ident,2))) + "\n" + 
	#"\t" + get_bin(checksum, 5) + "\t\t#checksum\t" + str(len(get_bin(checksum, 5))) + "\n" +  
	#"\t" + get_bin(channel_number,3) + "\t\t#channel_number\t" + str(len(get_bin(channel_number,3))) + "\n" +  
	#"\t" + get_bin(pulse_width,9) + "\t#pulse_width\t" + str(len(get_bin(pulse_width,9))) + "\n" +  
	#"\t" + get_bin(pulse_current,7) + "\t\t#pulse_current\t" + str(len(get_bin(pulse_current,7))) + "\n" 
	#) 
	binarized_cmd = get_bin(ident,2) + get_bin(checksum, 5) + get_bin(channel_number,3) + get_bin(pulse_width,9) + get_bin(pulse_current,7)
	cmd_pointer = 0
	new_cmd_pointer = 0
	proper_cmd= ["0" for x in range(32)]

	for c in proper_cmd:
    		if new_cmd_pointer == 0: #add a 1
    		        proper_cmd[new_cmd_pointer]="1"
    		elif new_cmd_pointer == (9-1) or new_cmd_pointer == (17-1) or new_cmd_pointer == (25-1): #add a 0 
    		        proper_cmd[new_cmd_pointer]="0"
    		elif new_cmd_pointer == (13-1) or new_cmd_pointer == (14-1): #add a X
    		        proper_cmd[new_cmd_pointer]="0"
    		else:
		        proper_cmd[new_cmd_pointer]=binarized_cmd[cmd_pointer]
 		        cmd_pointer+=1
                new_cmd_pointer+=1

        proper_bin_command = ''.join(map(str,proper_cmd))
	#print(proper_bin_command)

        hex_command = (hex(int(proper_bin_command, 2)).replace("0x",''))
	hex_command = hex_command.replace("L",'')
	#print(hex(int(proper_bin_command, 2)))
	return(binascii.unhexlify(hex_command))
# End of singlepulse.py
