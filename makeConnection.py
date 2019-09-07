#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, sys, base64, os, subprocess

from modules import knownHostsFile, rsaPublicKey, onError, runSubprocess

def selectConnectionType(f_key, connectionFile, show, verbose):
    connectionTypeNo = 0
    
    connectionTypes = ['ssh', 'sftp', 'scp', 'ssh -X', 'ssh -Y', 'ssh-copy-id']

    print("\nSelect connection type\n----------")
    for connectionType in connectionTypes:
        connectionTypeNo += 1
        print(" " + str(connectionTypeNo) + ": " + connectionType)
        
    print("\nEnter number:")
    while True:
        selection = input(" ? ")
        
        if not selection:
            print("You must select a number 1-" + str(connectionTypeNo) + "\nTry again")
        else:
            try:
                selection = int(selection)
            except:
                print("Only integers allowed\nTry again:")
            else:
                if selection <= 0 or selection > connectionTypeNo:
                    print("Number must be 1-" + str(connectionTypeNo))
                else:
                    break
            
    connectionType = connectionTypes[int(selection) - 1]
    
    if connectionType == "ssh":
        ip, port, userName, plainTextPass = selectConnection(f_key, connectionFile, show, connectionType, verbose)
        
        sshConnect(ip, port, userName, plainTextPass, verbose)
        #pxsshConnect(ip, port, userName, plainTextPass, verbose)
        #paramikoConnect(ip, port, userName, plainTextPass, verbose)
        
        sys.exit(0)
        
    elif connectionType == "ssh-copy-id":
        keyFile = sshCreateKey(verbose)
        if verbose:
            print("\n--- Will use public key at " + keyFile)
        
        ip, port, userName, plainTextPass = selectConnection(f_key, connectionFile, show, connectionType, verbose)

        sshCopyID(ip, port, userName, keyFile, verbose)
        
        sys.exit(0)
        
def sshCreateKey(verbose):
    if verbose:
        print("\n--- Checking if there is a key at " + rsaPublicKey)
        
    if os.path.isfile(rsaPublicKey):
        if verbose:
            print("    OK")
        keyFile = rsaPublicKey
    else:
        keyDir = os.path.dirname(rsaPublicKey)
        print("\nCould not find key file at " + 
              rsaPublicKey + 
              "\n\nIf file is at other location, state full path, \nor leave empty to create key pair in\n" + 
              rsaPublicKey)
        
        keyFile = input(" ? ")    
            
        if keyFile:
            if not os.path.isfile(keyFile):
                keyDir = os.path.dirname(keyFile)
                keyFile = os.path.splitext(keyFile)[0]
                print("\nCould not find that file either\nDo you want to create key pair at " + 
                      keyFile + "?")
                answer = input("n/Y")
                
                if answer.lower() != "n":
                    print("\nWill create key pair at " + keyFile + "\n\n----------")
                    
        else:
            keyFile = rsaPublicKey
            keyFile = os.path.splitext(keyFile)[0]
            print("\nWill create key pair at " + keyFile + "\n\n----------")
            
        keyDir = os.path.dirname(keyFile)
        
        if keyDir == "":
            keyDir = "./"
        
        if not os.path.isdir(keyDir):
            try:
                os.makedirs(keyDir, exist_ok=False)
            except:
                onError(6, ("Could not create directory " + keyDir))
        
        cmd = "ssh-keygen -f " + keyFile
        runSubprocess(cmd, verbose)
        
    return keyFile
    
def sshCopyID(ip, port, userName, keyFile, verbose):
    if verbose:
        print("\n--- Copying id ...")
    
    cmd = "ssh-copy-id -p " + port + " -i " + keyFile + " " + (userName + "@" + ip)
    runSubprocess(cmd, verbose)


def selectConnection(f_key, connectionFile, show, connectionType, verbose):
    connectionNo = 0
    userNo = 0
    connectionList =   []
    userList = []
    
    if verbose:
        print("\n--- Searching for sections in connections file")
        
    config = configparser.ConfigParser()
    
    config.read(connectionFile)  # read config file
    
    sections = config.sections()
    
    print("\nSelect host\n----------")
    
    for section in sections:
        connectionNo += 1
        
        hostName = config.get(section, 'hostname')
        port = config.get(section, 'port')
        
        print(" " + str(connectionNo) + ": " + section + ", " + hostName)
        connectionList.append({u'number': connectionNo, u'ip': section, u'host': hostName, u'port': port})
        
    print("\nEnter number:")
    while True:
        selection = input(" ? ")
        
        try:
            selection = int(selection)
        except:
            print("Only integers allowed\nTry again:")
        else:
            if selection <= 0 or selection > connectionNo:
                print("Number must be 1-" + str(connectionNo))
            else:
                break
            
    for connection in connectionList:
        if int(connection['number']) == selection:
            ip = connection['ip']
            host = connection['host']
        
    print("\nSelect user on " + ip + ", " + host + "\n----------")
        
    options = config.options(ip)
        
    userSet = False
    passwdSet = False
        
    for option in options:
        if option.startswith('username'):
            userNo += 1
            
            user = config.get(ip, option)
            userSet = True
        elif option.startswith('password'):
            passwd = config.get(ip, option)
            passwdSet = True
            
        if userSet and passwdSet:
            print(" " + str(userNo) + ": " + user)
            userList.append({u'number': userNo, u'user': user, u'passwd': passwd})
            userSet = False
            passwdSet = False
            
    print("\nEnter number:")
    while True:
        selection = input(" ? ")
        
        try:
            selection = int(selection)
        except:
            print("Only integers allowed\nTry again:")
        else:
            if selection <= 0 or selection > userNo:
                print("Number must be 1-" + str(userNo))
            else:
                break
        
    for user in userList:
        if int(user['number']) == selection:
            userName = user['user']
            passwd = user['passwd']
            break    
    
    print("\nWill connect to " + host + " at " + ip + " on port " + port + " as " + userName)
    
    plainTextPass = bytes(f_key.decrypt((passwd).encode())).decode("utf-8")
    
    if show:
        print("\nUse password '" + plainTextPass + "'")
        
    return ip, port, userName, plainTextPass    
        
def paramikoConnect(ip, port, userName, plainTextPass, verbose):
    if verbose:
        print("--- Connecting with paramiko ...")
        
    import paramiko
            
    #key = paramiko.RSAKey(data=base64.b64decode(b'AAA...'))
    client = paramiko.SSHClient()
    #client.get_host_keys().add(ip, 'ssh-rsa', key)
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    
    try:
        client.connect(ip, port=int(port), username=userName, password=plainTextPass)
    except paramiko.ssh_exception.SSHException as e:
        print("Error: \n" + str(e))
    else:
        stdin, stdout, stderr = client.exec_command('whoami')
        for line in stdout:
            print('... ' + line.strip('\n'))
        client.close()
        
def sshConnect(ip, port, userName, plainTextPass, verbose):
    if verbose:
        print("\n--- Connecting with ssh ...")
    
    cmd = "ssh " + ip + " -l " + userName + " -p " + port + " -o UserKnownHostsFile=" + knownHostsFile
    runSubprocess(cmd, verbose)
                
def pxsshConnect(ip, port, userName, plainTextPass, verbose):
    if verbose:
        print("--- Connecting with pxssh ...")
        
    from pexpect import pxssh
    
    print()
    
    try:                                                            
        s = pxssh.pxssh()
        s.login (ip, userName, plainTextPass, port=int(port))
        s.sendline ('uptime')   # run a command
        s.prompt()             # match the prompt
        #print(s.before)          # print everything before the prompt.
        pxsshPrint(s.before)
        print()
        s.sendline ('ls -l')
        s.prompt()
        #print(s.before)
        pxsshPrint(s.before)
        print()
        s.sendline ('df')
        s.prompt()
        pxsshPrint(s.before)
        #print(s.before)
        print()
        s.logout()
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(str(e))
            
def pxsshPrint(input):
    lines = input.split(b'\r\n')
    
    for line in lines:
        print(line.decode())
            
        
        
        
        
        
        
        
        
        
        
        