from __future__ import division
import pingparser
import os, sys, glob, re
from os.path import isfile


if __name__ == '__main__':
    i = 0.54
    jitter_file = open('/home/luca/workspace/interference_scenario/jitter_diff.dat', "w")
    delay_file = open('/home/luca/workspace/interference_scenario/delay_diff.dat', "w")
    packet_loss_file = open('/home/luca/workspace/interference_scenario/packet_loss_diff.dat', "w")

    os.chdir("/home/luca/stats/interference_scenario/")
    for my_file in sorted(glob.glob('*')):
        if isfile(my_file):
            print my_file
            with open (my_file, "r") as read_file:
                data=read_file.read().replace('\n', '')
                read_file.close()
                parsed_data = pingparser.parse(data)        
                #print parsed_data
                jitter = parsed_data.get('jitter')
                jitter_file.write(str(i) + " " + jitter + "\n")
                delay = parsed_data.get('avgping')
                delay_file.write(str(i) + " " + delay + "\n")
                packet_loss = 100 - (float(parsed_data.get('received', None)) * 100 / float(parsed_data.get('sent', None)))
                packet_loss_file.write(str(i) + " " + str(packet_loss) + "\n")
                i = i + 0.01