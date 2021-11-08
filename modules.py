#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, os, sys, subprocess

import socket

from pathlib import Path

from cryptography.fernet import Fernet

config = configparser.ConfigParser()  # define config file
config.read(
    "%s/config.ini" % os.path.dirname(os.path.realpath(__file__))
)  # read config file

# read variables from config file
knownhostsfile = config.get("paths", "knownhostsfile").strip()
rsapublickey = config.get("paths", "rsapublickey").strip()
settingsdir = config.get("paths", "settingsdir").strip()

connectionTypes = [
    x.strip() for x in config.get("variables", "connectiontypes").split(",")
]

mainWidth = config.get("gui", "mainwidth").strip()
mainHeight = config.get("gui", "mainheight").strip()
mainWH = mainWidth + "x" + mainHeight

homeDir = str(Path.home())

knownHostsFile = os.path.join(homeDir, knownhostsfile)
rsaPublicKey = os.path.join(homeDir, rsapublickey)
settingsDir = os.path.join(homeDir, settingsdir)

connectionFile = os.path.join(settingsDir, "connections")

# handle errors
def onError(errorCode, extra):
    print("\nError:")
    if errorCode == 1:  # print error information, print usage and exit
        print(extra)
        usage(errorCode)
    elif errorCode == 2:  # no argument given to option, print usage and exit
        print("No options given")
        usage(errorCode)
    elif errorCode in (3, 5, 6):  # print error information and exit
        print(extra)
        sys.exit(errorCode)
    elif errorCode in (4, 7):  # print error information and return running program
        print(extra)
        return


# print usage information
def usage(exitCode):
    print("\nUsage:")
    print("----------------------------------------")
    print("%s <options>" % sys.argv[0])
    print("\nOptions: ")
    print("  -c, --connect")
    print("    Connect to remote host")
    print("  -a, --add")
    print("    Add hosts, usernames etc.")
    print("  -e, --edit")
    print("    Edit hosts, usernames etc.")
    print("  -p, --print")
    print("    Prints all hosts, usernames etc. on screen")
    print("  -s, --show")
    print("    Shows passwords in plain text")
    print("  -v, --verbose")
    print("    Verbose output")
    print("  -h, --help")
    print("    Prints this")
    sys.exit(exitCode)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def getF_key(verbose):
    # check if key file exists
    keyFileLocation = os.path.join(settingsDir, "key")
    if verbose:
        print("--- Checking if key exists at\n    " + keyFileLocation)
    if os.path.isfile(keyFileLocation):
        if verbose:
            print("    OK")
        with open(keyFileLocation, "rb") as file_object:  # retrieve key
            key = file_object.read()
        if verbose:
            print("    Key value: " + str(key))
    else:
        key = createKeyFile(keyFileLocation, verbose)

    f_key = Fernet(key)

    return f_key


def createKeyFile(keyFileLocation, verbose):
    print("\nCreating key file at " + keyFileLocation)

    from cryptography.fernet import Fernet

    key = Fernet.generate_key()

    print("\nKey value: " + str(key))

    with open(keyFileLocation, "wb") as file_object:
        file_object.write(key)

    print("\nKey file written")

    return key


def runSubprocess(cmd, verbose):
    if verbose:
        print("\n--- Running subprocess")
        print("    Constructing command from \n    " + cmd + " ...")

    cmdList = cmd.split()

    if verbose:
        print("    Command list: \n        " + str(cmdList))

    print("\n" + cmdList[0] + " session starts\n----------")
    response = subprocess.run(cmdList)
    print("----------\n" + cmdList[0] + " session ended")

    returnCode = response.returncode
    if returnCode != 0:
        print("\nProcess exited uncleanly\nwith exit code " + str(response.returncode))


def encryptPassword(f_key, plainTextPass, show, verbose):
    if verbose:
        if show:
            print("\n--- Encrypting password " + plainTextPass)
        else:
            print("\n--- Encrypting password *****")

    encPasswd = f_key.encrypt(plainTextPass.encode()).decode()

    if verbose:
        print("\n--- Encrypted password: " + encPasswd)

    return encPasswd


def decryptPassword(f_key, cryptPasswd, verbose):
    if verbose:
        print("\n--- Decrypting password ...")
        print("    " + cryptPasswd)

    plainTextPass = bytes(f_key.decrypt(cryptPasswd.encode())).decode("utf-8")

    return plainTextPass


def findUserNo(ip, usernameFind, verbose):
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file

    options = config.options(ip)

    for option in options:
        if option.startswith("username"):
            username = config.get(ip, option)
            if username == usernameFind:
                userNo = option.lstrip("username")

    return userNo
