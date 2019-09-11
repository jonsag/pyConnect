#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, os

from modules import (knownHostsFile, rsaPublicKey, onError, runSubprocess, decryptPassword, 
                     connectionTypes)

def selectConnectionType(f_key, connectionFile, show, verbose):
    connectionTypeNo = 0

    print("\nSelect connection type\n----------")
    for connectionType in connectionTypes:
        connectionTypeNo += 1
        print(" " + str(connectionTypeNo) + ": " + connectionType)
        
    print("\nEnter number:")
    while True:
        selection = input("(1) ? ")
            
        if selection:
            try:
                selection = int(selection)
            except:
                print("Only integers allowed\nTry again:")
            else:
                if selection <= 0 or selection > connectionTypeNo:
                    print("Number must be 1-" + str(connectionTypeNo) + "\nTry again")
                else:
                    break
        else:
            selection = 1
            break
            
    connectionType = connectionTypes[int(selection) - 1]
    
    # ssh
    if connectionType == "ssh":
        ip, host, port, userNo, username, cryptPasswd = selectConnection(f_key, connectionFile, show, verbose)
        if userNo >= 0:
            print("\nWill connect to " + host + " at " + ip + " on port " + port + 
                  " as " + username + " who has user index " + str(userNo))
            if show:
                print("\nUse password '" + decryptPassword(f_key, cryptPasswd, verbose) + "'")
            sshConnect(ip, port, username, "", verbose)
        else:
            print("\nCan't make a connection  to " + host)
    
    # ssh -X   
    elif connectionType == "ssh -X":
        ip, host, port, userNo, username, cryptPasswd = selectConnection(f_key, connectionFile, show, verbose)
        if userNo >= 0:
            print("\nWill connect to " + host + " at " + ip + " on port " + port + 
                  " as " + username + " who has user index " + str(userNo))
            if show:
                print("\nUse password '" + decryptPassword(f_key, cryptPasswd, verbose) + "'")            
            sshConnect(ip, port, username, "-X", verbose)
        else:
            print("\nCan't make a connection")
    
    # ssh -Y
    elif connectionType == "ssh -Y":
        ip, host, port, userNo, username, cryptPasswd = selectConnection(f_key, connectionFile, show, verbose)
        if userNo >= 0:
            print("\nWill connect to " + host + " at " + ip + " on port " + port + 
                  " as " + username + " who has user index " + str(userNo))
            if show:
                print("\nUse password '" + decryptPassword(f_key, cryptPasswd, verbose) + "'")
            sshConnect(ip, port, username, "-Y", verbose)
        else:
            print("\nCan't make a connection to " + host)
            
    # sftp        
    elif connectionType == "sftp":
        ip, host, port, userNo, username, cryptPasswd = selectConnection(f_key, connectionFile, show, verbose)
        if userNo >= 0:
            print("\nWill connect to " + host + " at " + ip + " on port " + port + 
                  " as " + username + " who has user index " + str(userNo))
            if show:
                print("\nUse password '" + decryptPassword(f_key, cryptPasswd, verbose) + "'")
            sftpConnect(f_key, ip, port, username, cryptPasswd, verbose)
        else:
            print("\nCan't make a connection to " + host)             
          
    # ssh-copy-id  
    elif connectionType == "ssh-copy-id":
        keyFile = sshCreateKey(verbose)
        if verbose:
            print("\n--- Will use public key at " + keyFile)
        ip, host, port, userNo, username, cryptPasswd = selectConnection(f_key, connectionFile, show, verbose)
        if userNo >= 0:
            print("\nWill transfer key from " + keyFile + 
                  " \nto " + host + " at " + ip + " on port " + port + " as " + username)
            if show:
                print("\nUse password '" + decryptPassword(f_key, cryptPasswd, verbose) + "'")
            sshCopyID(ip, port, username, keyFile, verbose)
        else:
            print("\nCan't transfer key")
    
    # run command on multiple hosts
    elif connectionType == "run command on multiple hosts":
        print("\nEnter command:")
        while True:
            cmd = input("[uptime] ? ")
                        
            if cmd:
                break
            else:
                #print("You must enter a command\nTry again")
                cmd = "uptime"
                break
        
        connectionList = []
        print("Select connections to run command")
        while True:
            ip, host, port, userNo, username, cryptPasswd = selectConnection(f_key, connectionFile, show, verbose)
            
            connectionList.append({'ip': ip, 'host': host, 'port': port, 'userNo': userNo, 'username': username, 'cryptPasswd': cryptPasswd})
            print("\nConnections added:")
            for connection in connectionList:
                print("    Host: " + connection['host'] + " User: " + connection['username'])
            
            print("\nDo you want to add another connection")
            add = input("(y/N) ? ")
            if add.lower() != "y":
                break
            
        for connection in connectionList:
            if userNo >= 0:
                if connection['username'] == "root":
                    prompt = "#"
                else:
                    prompt = "$"
                if verbose:
                    print("\n--- Will connect to " + connection['host'] + 
                          " at " + connection['ip'] + 
                          " on port " + connection['port'] + 
                          " as " + connection['username'] + 
                          " who has user index " + str(connection['userNo']))
                    if show:
                        print("    Use password '" + decryptPassword(f_key, connection['cryptPasswd'], verbose) + "'")
                outputList, errorList = paramikoRunCmd(f_key, connection['ip'], connection['port'], connection['username'], connection['cryptPasswd'], cmd, verbose)
                print("\nOutput from " + connection['username'] + "@" + connection['host'] + " " + prompt)
                for output in outputList:
                    print(prompt + " " + output.strip('\n'))
            else:
                print("\nCan't make a connection to " + host)
        
        
                
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
    
def sshCopyID(ip, port, username, keyFile, verbose):
    if verbose:
        print("\n--- Copying id ...")
    
    cmd = "ssh-copy-id -p " + port + " -i " + keyFile + " " + (username + "@" + ip)
    runSubprocess(cmd, verbose)


def selectConnection(f_key, connectionFile, show, verbose):
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
        
        hostname = config.get(section, 'hostname')
        port = config.get(section, 'port')
        
        print(" " + str(connectionNo) + ": " + section + ":" + port + ", " + hostname)
        connectionList.append({u'number': connectionNo, u'ip': section, u'host': hostname, u'port': port})
        
    print("\nEnter number:")
    while True:
        ipSelection = input("(1) ? ")
        
        if ipSelection:
            try:
                ipSelection = int(ipSelection)
            except:
                print("\nOnly integers allowed\nTry again:")
            else:
                if ipSelection <= 0 or ipSelection > connectionNo:
                    print("Number must be 1-" + str(connectionNo))
                else:
                    break
        else:
            ipSelection = 1
            break
            #print("\nSelect number 1-" + str(connectionNo) + "\nTry again")
            
    for connection in connectionList:
        if int(connection['number']) == ipSelection:
            ip = connection['ip']
            host = connection['host']
            port = connection['port']
        
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
            
    if userNo >= 1:
        print("\nEnter number:")
        while True:
            userSelection = input("(1) ? ")
            
            if userSelection:
                try:
                    userSelection = int(userSelection)
                except:
                    print("\nOnly integers allowed\nTry again:")
                else:
                    if userSelection <= 0 or userSelection > userNo:
                        print("Number must be 1-" + str(userNo))
                    else:
                        break
            else:
                userSelection = 1
                break
                #print("\nSelect number 1-" + str(userNo) + "\nTry again")
            
        for user in userList:
            if int(user['number']) == userSelection:
                username = user['user']
                cryptPasswd = user['passwd']
                break   
    else:
        print("\nSorry. No users added to this connection")
        userSelection = 0
        username = ""
        cryptPasswd = ""
        
    
    if verbose:
        print("\n--- Selections:")
        print("    IP:          " + ip)
        print("    Hostname:    " + host)
        print("    Port:        " + port)
        if userNo >= 1:
            print("    User number: " + str((userSelection - 1)))
            print("    Username:    " + username)
            if show:
                print("    Password:    " + decryptPassword(f_key, cryptPasswd, verbose))
        
    return ip, host, port, userSelection - 1, username, cryptPasswd   
        
def paramikoRunCmd(f_key, ip, port, username, cryptPasswd, cmd, verbose):
    import paramiko, base64
    
    outputList = []
    errorList = []
    
    if verbose:
        print("\n--- Connecting with paramiko ...")
    
    rsaKeyFile = rsaPublicKey.strip(".pub")
    if verbose:
        print("    Using keyfile at " + rsaKeyFile)
    
    if verbose:
        print("    Generating host keys ...")
    host_key = paramiko.RSAKey.from_private_key_file(rsaKeyFile)
    public_host_key = paramiko.RSAKey(data=host_key.asbytes())
    
    if verbose:
        print("    Setting up client ...")
    client = paramiko.SSHClient()
    
    #if verbose:
    #    print("    Adding host keys ...")
    #client.get_host_keys().add(ip, "ssh-rsa", public_host_key)
    
    if verbose:
        print("    Setting missing host key policy ...")                           
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    if verbose:
        print("    Loading known hosts from " + knownHostsFile + " ...")
    client.load_host_keys(knownHostsFile)
    
    if verbose:
        print("    Connecting ...")
    try:
        client.connect(ip, port=int(port), username=username, password=decryptPassword(f_key, cryptPasswd, verbose))
    except paramiko.ssh_exception.SSHException as e:
        onError(7, str(e))
        stdout = ""
        stderr = ""
    else:
        if verbose:
            print("    Running command ...")
        stdin, stdout, stderr = client.exec_command(cmd)
        
        if verbose:
            print("\n--- Output:")
        for line in stdout:
            outputList.append(line)
            if verbose:
                print('    ' + line.strip('\n'))
        
        if verbose:
            print("\n--- Error:")
        for line in stderr:
            errorList.append(line)
            if verbose:
                print('    ' + line.strip('\n'))
        
        if verbose:
            print("\n--- Closing client ...")
        client.close()
        
    return outputList, errorList

def sshConnect(ip, port, username, extra, verbose):
    if verbose:
        print("\n--- Connecting with ssh " + extra + " ...")
    
    cmd = "ssh " + ip + " -l " + username + " -p " + port + " -o UserKnownHostsFile=" + knownHostsFile + " " + extra
    runSubprocess(cmd, verbose)
                
def pxsshConnect(f_key, ip, port, username, cryptPasswd, verbose):
    if verbose:
        print("--- Connecting with pxssh ...")
        
    from pexpect import pxssh
    
    print()
    
    try:                                                            
        s = pxssh.pxssh()
        s.login (ip, username, decryptPassword(f_key, cryptPasswd, verbose), port=int(port))
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
            
def pxsshPrint(output):
    lines = output.split(b'\r\n')
    
    for line in lines:
        print(line.decode())
        
def sftpConnect(f_key, ip, port, username, cryptPasswd, verbose):
    if verbose:
        print("\n--- Connecting with sftp ...")
    
    cmd = "sftp " + " -P " + port + " -o UserKnownHostsFile=" + knownHostsFile + " " + username + "@" + ip
    runSubprocess(cmd, verbose)
            
        
        
        
        
        
        
        
        
        
        
        