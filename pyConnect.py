#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

# import modules
import sys, getopt, os

from cryptography.fernet import Fernet

# import modules from file modules.py
from modules import onError, usage, createKeyFile

from createConnection import createConnection

from printConnections import showConnections

# handle options and arguments passed to script
try:
    myopts, args = getopt.getopt(sys.argv[1:],
                                 'apsvh',
                                 ['add', 'print', 'show', 'verbose', 'help'])

except getopt.GetoptError as e:
    onError(1, str(e))

# if no options passed, then exit
if len(sys.argv) == 1:  # no options passed
    onError(2, 2)
    
createNewConnection = False
printConnections = False    
show = False
verbose = False
            
# interpret options and arguments
for option, argument in myopts:
    if option in ('-a', '--add'):  # add connections
        createNewConnection = True
    elif option in ('-p', '--print'):  # print connections
        printConnections = True    
    elif option in ('-s', '--show'):  # print passwords on screen
        show = True
    elif option in ('-v', '--verbose'):  # verbose output
        verbose = True
    elif option in ('-h', '--help'):  # display help text
        usage(0)
        
# check if key file exists
keyFileLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), "key")
if verbose:
    print("--- Checking if key exists at\n" + keyFileLocation)
if os.path.isfile(keyFileLocation):
    if verbose:
        print("+++ Key file exists")
    with open(keyFileLocation, 'rb') as file_object: # retrieve key
        key = file_object.read()
    if verbose:
        print("+++ Key value: " + str(key))
        print("    Key Type: " + str(type(key)))
else:
    key = createKeyFile(keyFileLocation, verbose)
    

f_key = Fernet(key)

if createNewConnection and printConnections:
    onError(3, "Only one of -a and -p can be stated")

connectionFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "connections")

if createNewConnection:
    createConnection(f_key, connectionFile, show, verbose)

if printConnections:
    showConnections(f_key, connectionFile, show, verbose)