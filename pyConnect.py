#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

# import modules
import sys, getopt, os

from cryptography.fernet import Fernet

# import modules from file modules.py
from modules import onError, usage, settingsDir, getKey

from createConnection import createConnection

from viewConnections import viewConnections

from makeConnection import selectConnectionType

from editConnections import editConnections

create = False
view = False    
show = False
connect = False
edit = False
verbose = False
selections = 0

# handle options and arguments passed to script
try:
    myopts, args = getopt.getopt(sys.argv[1:],
                                 'apscevh',
                                 ['add', 'print', 'show', 'connect', 'edit', 'verbose', 'help'])

except getopt.GetoptError as e:
    onError(1, str(e))

# if no options passed, then exit
if len(sys.argv) == 1:  # no options passed
    print("Automatically selecting to connect")
    connect = True
    #onError(2, 2)

# interpret options and arguments
for option, argument in myopts:
    if option in ('-a', '--add'):  # add connections
        create = True
        selections += 1
    elif option in ('-p', '--print'):  # print connections
        view = True
        selections += 1  
    elif option in ('-s', '--show'):  # print passwords on screen
        show = True
    elif option in ('-c', '--connect'):  # connect
        connect = True
        selections += 1
    elif option in ('-e', '--edit'):  # edit connections
        edit = True
        selections += 1
    elif option in ('-v', '--verbose'):  # verbose output
        verbose = True
    elif option in ('-h', '--help'):  # display help text
        usage(0)
        
# check if settings directory exists
if not os.path.isdir(settingsDir):
    if verbose:
        print("\n--- Directory for settings \n    " + settingsDir + ",\n    does not exist \n    Creating it ...")
    try:
        os.makedirs(settingsDir, exist_ok=False)
    except:
        onError(6, ("Could not create directory " + settingsDir))
                
key = getKey(verbose)    

f_key = Fernet(key)

if selections >= 2:
    onError(3, "Only one of -a, -p, -c and -e can be stated")

connectionFile = os.path.join(settingsDir, "connections")
if not os.path.isfile(connectionFile):
    print("\nYou haven't created any connections yet\nLet's start with adding some\nThen rerun this program")
    create = True
    view = False
    connect = False
    edit = False
    
if create:
    createConnection(f_key, connectionFile, show, verbose)

if view:
    viewConnections(f_key, connectionFile, show, verbose)
    
if connect:
    selectConnectionType(f_key, connectionFile, show, verbose)
    
if edit:
    editConnections(f_key, connectionFile, show, verbose)    
    
    
    