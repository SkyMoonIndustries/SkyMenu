#!/usr/bin/python3

import subprocess
import time
time.sleep(90)
try:
    cmd = "ps -t | grep skymenu.py | grep -v grep"
    pid = subprocess.check_output(cmd, shell = True )
    pid = pid.split(" ")
    #print(pid[1])
    pidnumber=pid[1]
    pidname=pid[len(pid)-1]
    #nb = len(pid)
    #print(nb)
    #print(pid[nb-1])
    print(pidnumber + " => " + pidname)
    cmd="kill "+ pidnumber + " &"
    exe = subprocess.check_output(cmd, shell = True )
    cmd="python3 /home/skymoon/SkyMenu/skymenu.py &"
    exe = subprocess.check_output(cmd, shell = True )
    exit()
except:
    print("no pid")
    cmd="python3 /home/skymoon/SkyMenu/skymenu.py &"
    exe = subprocess.check_output(cmd, shell = True )
    exit()