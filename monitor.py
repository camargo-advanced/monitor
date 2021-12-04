#!/usr/bin/env python3
#
# Marcelo Camargo, December 1st, 2021
# 
# Monitors specified targets at the operating system level.
# Outputs to file monitor.json in the python script installation path.
# Please update the monitor.conf with your targets.
#
# To execute, please add the folowing line to crontab:
#   * * * * * <absolute_path>/monitor.py 
# in Ubuntu, you can use the folowing command to edit crontab:
#   sudo crontab -e
# Enjoy !

import subprocess  
import datetime
from time import sleep
import os
import json

real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)
json_filename = dir_path + '/monitor.json'
log_filename = dir_path + '/monitor.log'
conf_filename = dir_path + '/monitor.conf'

def get_processes():
    proc = subprocess.Popen(['ps', '-aux'], 
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE) 
    out, err = proc.communicate()
    lines = str(out)[2:-3].split('\\n')
    processes = []
    header = True
    for line in lines:
        if header: # skip header
            header = False
            continue
        line_split = line.split()
        try:
            cmd = line_split[10] + " " + line_split[11]
        except IndexError:
            cmd = line_split[10]
        process = {
            #'user':line_split[0], 
            'pid':line_split[1],
            #'cpu':line_split[2], 'mem':line_split[3],
            #'vsz':line_split[4], 'rss':line_split[5],
            #'tty':line_split[6], 'stat':line_split[7],
            #'start':line_split[8], 'time':line_split[9],
            'cmd':cmd,
        }   
        processes.append(process)
    return processes

def get_elements_for_target(target, list_of_elements):
    result_list = []
    for element in list_of_elements:
        if element['cmd'].find(target) != -1: 
            result_list.append(element)
    return result_list

def update_tracking(targets, processes, tracking):
    for target in targets:                                              
        runnings = get_elements_for_target(target, processes)
        tracks = get_elements_for_target(target, tracking)
        
        # stop tracking not running processes
        for track in tracks:
            if track not in runnings:
                write_log('Stopped tracking ' + str(track))
                tracking.remove(track)
        
        # start tracking new running processes
        num = len(tracks)
        for running in runnings:
            if running not in tracks:
                num = num + 1
                write_log('Started tracking (' + str(num) + ")" + str(running))
                tracking.append(running)
        
def write_log(msg):
    now = datetime.datetime.now()
    append_file(log_filename, '---> [' + now.strftime("%c") + '] ' + msg)

def append_file(filename, data):
    f = open(filename, 'a')
    f.write(data + '\n')
    f.flush()
    f.close()       
        
def jsondump_file(filename, data):
    f = open(filename, 'w')
    json.dump(data, f)
    f.flush()
    f.close()    

def jsonload_file(filename):
    try:
        f = open(filename, 'r')
        data = json.load(f)
        f.flush()
        f.close()
        return data
    except FileNotFoundError:
        return []

# main code - starting point
targets = jsonload_file(conf_filename)
tracking = jsonload_file(json_filename)

n = 12 # 12 x 5 seconds = 60 seconds
while n > 0:
	n = n - 1
	write_log('scanning processes...')
	processes = get_processes()
	update_tracking(targets, processes, tracking)
	jsondump_file(json_filename, tracking)
	sleep(5)
