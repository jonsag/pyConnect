#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, os, sys

import socket

from pathlib import Path

config = configparser.ConfigParser()  # define config file
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__)))  # read config file

# read variables from config file
knownhostsfile = config.get('paths', 'knownhostsfile').strip()
rsapublickey = config.get('paths', 'rsapublickey').strip()
settingsdir = config.get('paths', 'settingsdir').strip()

homeDir = str(Path.home())

knownHostsFile = os.path.join(homeDir, knownhostsfile)
rsaPublicKey = os.path.join(homeDir, rsapublickey)
settingsDir = os.path.join(homeDir, settingsdir)

# handle errors
def onError(errorCode, extra):
    print("\nError:")
    if errorCode == 1: # print error information, print usage and exit
        print(extra)
        usage(errorCode)
    elif errorCode == 2: # no argument given to option, print usage and exit
        print("No options given")
        usage(errorCode)
    elif errorCode in (3, 5, 6): # print error information and exit
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

def createKeyFile(keyFileLocation,verbose):
    print("\nCreating key file at " + keyFileLocation )
    
    #import random
    #key = str(random.getrandbits(128))
    
    #import uuid
    #key = uuid.uuid4().hex
    
    #import binascii, os
    #key = str(binascii.hexlify(os.urandom(16)))

    #import secrets
    #key = secrets.token_hex(nbytes=16)
    
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()

    print("\nKey value: " + str(key))
    
    with open(keyFileLocation, 'wb') as file_object:
        file_object.write(key)
        
    print("\nKey file written")
    
    return key