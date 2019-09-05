#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import socket, sys, ipaddress, configparser

from getpass import getuser, getpass

#from cryptography.fernet import Fernet

from modules import get_ip

def createConnection(f_key, connectionFile, show, verbose):
    print("\nCreate new connection\n----------")
    
    defaultIP = get_ip()
    defaultPort = "22"
    defaultUser = getuser() 
    defaultPasswd = "xxx"
    
    while True:
        
        # input ip
        while True:
            print("\nRemote IP")
            ip = input("[" + defaultIP + "] ? ")
            
            if not ip:
                ip = defaultIP
            else:
                defaultIP = ip       
            
            if verbose:
                print("--- Checking if IP is valid ...")
            try:
                ipaddress.ip_address(ip)
                if verbose:
                    print("+++ Correct!")
                break
            except ValueError:
                print("\n" + ip + " is not a valid IP\nTry again")
            except:
                print("\n" + ip + " is a bad input\nTry again")
                
        #input port
        while True:
            print("\nRemote port")
            port = input("[" + defaultPort + "] ? ")
            
            if not port:
                port = defaultPort
            
            try:
                port = int(port)
            except:
                print("\n" + str(port) + "is not an integer\bTry again")
                            
            if verbose:
                print("--- Checking if port is valid ...")
            if port >= 0 and port <= 65535:
                if verbose:
                    print("+++ Correct")
                break
            else:
                print("\n" + str(port) + " is outside the range 0-65535\nTry again")
        
        userNo = 0
        userList = []
        passwdList = []
        encPasswdList = []
        while True: 
            userNo += 1
            
            #input username
            while True:
                print("\nUsername " + str(userNo))
                userName = input("[" + defaultUser + "] ? ")
                
                if not userName:
                    userName = defaultUser
                    
                if userName in userList:
                    print("\nUsername already in list\nTry again")
                else:
                    userList.append(userName)
                    break            
    
            #input password
            while True:
                print("\nPassword " + str(userNo))
                if show:
                    passwd1 = input("[" + defaultPasswd + "] ? ")
                else:
                    passwd1 = getpass("[" + defaultPasswd + "] ? ")
                
                if not passwd1:
                    passwd1 = defaultPasswd
                    
                print("Enter password " + str(userNo) + " again")
                if show:
                    passwd2 = input("[" + defaultPasswd + "] ? ")
                else:
                    passwd2 = getpass("[" + defaultPasswd + "] ? ")
                
                if not passwd2:
                    passwd2 = defaultPasswd
                    
                if passwd1 == passwd2:
                    passwdList.append(passwd1)
                    break
                else:
                    print("\nPasswords do not match\nTry again")
                
            print ("\nDo you like to add another user")
            addUser = input("(y/N) ? ")
            
            if addUser.lower() != "y":
                break
            else:
                userName = ""
                passwd1 = ""
                passwd2 = ""
            
        # display all values and ask if correct
        print("\nNew connection:\n----------")
        print("IP:   " + ip)
        print("Port: " + str(port))
        
        for i in range(0, userNo):
            print("\nUser " + str(i + 1) + ": " + userList[i])
            print("Pass " + str(i + 1) + ": " + "*" * len(passwdList[i]))
        print("\nIs this correct")
        correct = input("(Y/n/q) ? ")
        
        if correct.lower() == "q":
            print("\nExiting ...")
            sys.exit(0)
        elif correct.lower() != "n":
            break
        
    # encrypt passwords
    if verbose:
        print("\n--- Encrypting passwords ...")
    for i in range(0, userNo):
        encPasswdList.append(f_key.encrypt(passwdList[i].encode()))
    
    if verbose:
        for i in range(0, userNo):
            enc = encPasswdList[i]
            print("\n--- Encrypted password " + str(i + 1) + ": " + str(enc))
            if show:
                dec = f_key.decrypt(enc)
                #print("--- Decrypted password " + str(i + 1) + ": " + str(dec))
                plain = bytes(dec).decode("utf-8")
                print("--- Plain text password " + str(i + 1) + ": " + str(plain))
        
    print("\nAdding new connection ...") 
    
    writeConnection(connectionFile, ip, port, userNo, userList, encPasswdList, verbose)
    
def writeConnection(connectionFile, ip, port, userNo, userList, passwdList, verbose):
    exUsers = 0
    
    config = configparser.ConfigParser()
    
    config.read(connectionFile)  # read config file

    if verbose:
        print("Adding " + str(userNo) + " users")

    # read variables from config file
    try:
        config.add_section(ip)
    except configparser.DuplicateSectionError:
        print("\nIP " + ip + " already exist")
        
    try:
        oldPort = config.get(ip, 'port')                
    except:
        config[ip]['port'] = str(port)
    else:
        print("Port is already set to " + oldPort)
        if oldPort != str(port):
            print("Updating port with " + str(port))
            config.set(ip, 'port', str(port))
            
        options = config.options(ip)
        
        for option in options:
            if option.startswith('username'):
                exUsers += 1
                
            for i in range(0, exUsers):
                oldUser = config.get(ip, 'username' + str(i))
                for userName in userList:
                    if oldUser == userName:
                        print("User " + userName + " already exists")
                        userList.remove(userName)
                        userNo -= 1
                        print("Users left to add: " + str(userNo))
    
        print("There is already " + str(exUsers) + " users for that IP")
        
    if verbose:
        print("\n --- Adding connection ...")
        print("     IP:         " + ip)
        print("     Port:       " + str(port))    
    
    if userNo == 0:
        print("No users left to add")
    else:
        for i in range(0 + exUsers, userNo + exUsers):
            if verbose:
                print("     User " + str(i + 1) + ":     " + userList[i - exUsers])
                print("     Password " + str(i + 1) + ": " + str(passwdList[i - exUsers]))
            config[ip]['username' + str(i)] = userList[i - exUsers]
            passBytes = passwdList[i - exUsers]
            passString = passBytes.decode()
            config[ip]['password' + str(i)] = passString
    
    with open(connectionFile, 'w') as configfile:
        config.write(configfile)
        
    
    
    
    
    
    
    