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
db_file = dir_path + '/monitor.json'
log_file = dir_path + '/monitor.log'
conf_file = dir_path + '/monitor.conf'

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
            cmd = line_split[10] + line_split[11]
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

def get_running_processes_for_target(target, processes):
    runnings = []
    for process in processes:
        if process['cmd'].find(target) != -1: 
            runnings.append(process)
    return runnings

def get_tracks_for_target(target, tracking):
    tracks = []
    for track in tracking:
        if track['cmd'].find(target) != -1:
            tracks.append(track)
    return tracks

def update_tracking(targets, processes, tracking):
    for target in targets:                                              
        runnings = get_running_processes_for_target(target, processes)
        tracks = get_tracks_for_target(target, tracking)
        
        # stop tracking not running processes
        for track in tracks:
            if track not in runnings:
                tracking.remove(track)
                show_msg('Stopped tracking ' + str(track))
        
        # start tracking new running processes
        for running in runnings:
            if running not in tracks:
                tracking.append(running)
                show_msg('Started tracking ' + str(running))

def write_log(msg):
    with open(log_file, 'a') as f:
        f.write(msg + '\n')
        
def show_msg(msg):
    now = datetime.datetime.now()
    write_log('---> [' + now.strftime("%c") + '] ' + msg)

def save_db(data):
    with open(db_file, 'w') as f:
        json.dump(data, f)

def load_db():
    try:
        with open(db_file) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []

def load_conf():
    try:
        with open(conf_file) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []
        
# main code - starting point
targets = load_conf()
tracking = load_db()

n = 12 # 12 x 5 seconds = 60 seconds
while n > 0:
	n = n - 1
	show_msg('scanning processes...')
	processes = get_processes()
	update_tracking(targets, processes, tracking)
	save_db(tracking)
	sleep(5)
