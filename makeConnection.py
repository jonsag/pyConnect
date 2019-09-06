#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, sys, base64, os



def makeConnection(f_key, connectionFile, show, verbose):
    connectionNo = 0
    userNo = 0
    connectionList =   []
    userList = []
    
    if verbose:
        print("\n--- Searching for sections in connections file")
        
    config = configparser.ConfigParser()
    
    config.read(connectionFile)  # read config file
    
    sections = config.sections()
    
    for section in sections:
        connectionNo += 1
        
        hostName = config.get(section, 'hostname')
        port = config.get(section, 'port')
        
        print("\n" + str(connectionNo) + ": " + section + ", " + hostName)
        connectionList.append({u'number': connectionNo, u'ip': section, u'host': hostName, u'port': port})
        
    print("\nEnter number:")
    while True:
        selection = input("? ")
        
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
        
    print("\nUsers on " + ip + ", " + host)
        
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
            print("\n" + str(userNo) + " " + user)
            userList.append({u'number': userNo, u'user': user, u'passwd': passwd})
            userSet = False
            passwdSet = False
            
    print("\nEnter number:")
    while True:
        selection = input("? ")
        
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
        print("using password " + plainTextPass)
    
    pxsshConnect(ip, port, userName, plainTextPass, verbose)
    
    paramikoConnect(ip, port, userName, plainTextPass, verbose)   
    
        
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
        
    sys.exit(0)

def sshConnect(ip, port, userName, plainTextPass, verbose):
    if verbose:
        print("--- Connecting with ssh ...")
        
def pxsshConnect(ip, port, userName, plainTextPass, verbose):
    if verbose:
        print("--- Connecting with pxssh ...")
        
    from pexpect import pxssh
    
    print()
    
    try:                                                            
        s = pxssh.pxssh()
        s.login (ip, userName, plainTextPass)
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
        
    sys.exit(0)
    
def pxsshPrint(input):
    lines = input.split(b'\r\n')
    
    for line in lines:
        print(line.decode())
            
        
        
        
        
        
        
        
        
        
        
        