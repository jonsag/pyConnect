#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import socket, sys, ipaddress

from getpass import getuser, getpass

from modules import get_ip

def createConnection(verbose):
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
                passwd1 = getpass("[" + defaultPasswd + "] ? ")
                
                if not passwd1:
                    passwd1 = defaultPasswd
                    
                print("Enter password " + str(userNo) + " again")
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
        
    print("\nAdding new connection ...") 