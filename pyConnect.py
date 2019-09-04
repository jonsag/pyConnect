#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

# import modules
import sys, getopt, os

# import modules from file modules.py
from modules import onError, usage

from createConnection import createConnection

from createHash import createHashFile

# handle options and arguments passed to script
try:
    myopts, args = getopt.getopt(sys.argv[1:],
                                 'cvh',
                                 ['verbose', 'help'])

except getopt.GetoptError as e:
    onError(1, str(e))

# if no options passed, then exit
if len(sys.argv) == 1:  # no options passed
    onError(2, 2)
    
createNewConnection = False    
verbose = False
            
# interpret options and arguments
for option, argument in myopts:
    if option in ('-c', '--create'):  # verbose output
        createNewConnection = True
    elif option in ('-v', '--verbose'):  # verbose output
        verbose = True
    elif option in ('-h', '--help'):  # display help text
        usage(0)
        
# check if hash file exists
location = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hash")
if verbose:
    print("Checking if hash exists at\n" + location)
if os.path.isfile(location):
    if verbose:
        print("hash file exists")
else:
    createHashFile(location, verbose)
        
if createNewConnection:
    createConnection(verbose)
