#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tcp_cdciel.py


import socket               # Import socket module
import time

s = socket.socket()         # Create a socket object
#~ host = "127.0.0.1" #socket.gethostname() # Get local machine name
#~ port = 3292                # Reserve a port for your service.
host = "192.168.2.6" #socket.gethostname() # Get local machine name
port = 7624                     # Reserve a port for your service.

s.connect((host, port))


while 1:
    time.sleep(2)
    message = "Telescope Simulator.EQUATORIAL_EOD_COORD.RA"
    #~ message = "indi_getprop -h 192.168.2.6 | grep EOD"
    #~ print 'sending "%s"' % message.strip(' \t\n\r')
    s.sendall(message)
    line = s.recv(1024)
    print line.strip()
#~ s.close
#~
#~
#~ def main():
#~
	#~ return 0
#~
#~ if __name__ == '__main__':
	#~ main()

