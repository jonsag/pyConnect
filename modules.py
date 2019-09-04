#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, os, sys

import socket

config = configparser.ConfigParser()  # define config file
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__)))  # read config file

# read variables from config file
var = config.get('header', 'var').strip()

# handle errors
def onError(errorCode, extra):
    print("\nError:")
    if errorCode == 1: # print error information, print usage and exit
        print(extra)
        usage(errorCode)
    elif errorCode == 2: # no argument given to option, print usage and exit
        print("No options given")
        usage(errorCode)
    elif errorCode == 3: # print error information and exit
        print(extra)
        sys.exit(errorCode)
    elif errorCode == 4: # print error information and return running program
        print(extra)
        return
        
# print usage information        
def usage(exitCode):
    print("\nUsage:")
    print("----------------------------------------")
    print("%s " % sys.argv[0])

    sys.exit(exitCode)
    
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

