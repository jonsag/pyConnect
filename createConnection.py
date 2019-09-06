#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import sys, ipaddress, configparser, socket

from getpass import getuser, getpass

#from cryptography.fernet import Fernet

from modules import get_ip

def createConnection(f_key, connectionFile, show, verbose):
    print("\nCreate new connection\n----------")
    
    defaultIP = get_ip() # this computers IP
    defaultHostName = socket.gethostname() # this host name
    defaultPort = "22"
    defaultUser = getuser() # user running this script
    defaultPasswd = "xxx"
    
    while True: # run until all users is added
        while True: # input ip
            print("\nRemote IP")
            ip = input("[" + defaultIP + "] ? ")
            
            if not ip: # if no IP stated, accept default IP
                ip = defaultIP
            else:
                defaultIP = ip # if IP is given default IP is now the given one
            
            if verbose:
                print("--- Checking if IP is valid ...")
                
            try:
                ipaddress.ip_address(ip) # raises an exception if IP is not correct
            except ValueError:
                print("\n" + ip + " is not a valid IP\nTry again")
            except:
                print("\n" + ip + " is a bad input\nTry again")
            else:
                if verbose:
                    print("+++ Correct!")
                break # break out of while loop
            
        while True: #input host name
            print("\nHost name")
            if ip != get_ip():
                defaultHostName = socket.gethostbyaddr(ip)[0]
            hostName = input("[" + defaultHostName + "] ? ")
            
            if not hostName: # if no host name stated use default host name
                hostName = defaultHostName
            else:
                defaultHostName = hostName # if host name is given default host name is now the given one
                
            break # break out of while loop
                
        while True: #input port
            print("\nRemote port")
            port = input("[" + defaultPort + "] ? ")
            
            if not port: # if no port stated use default port
                port = defaultPort
            else:
                defaultPort = port # if port is given default port is now the given one
            
            try:
                port = int(port) # raises an exception if port is not an integer
            except:
                print("\n" + str(port) + "is not an integer\bTry again")
                            
            if verbose:
                print("--- Checking if port is valid ...")
            if port >= 0 and port <= 65535: # port must be between 0 and 65535
                if verbose:
                    print("+++ Correct")
                break # break out of while loop
            else:
                print("\n" + str(port) + " is outside the range 0-65535\nTry again")
        
        userNo = 0 # stores number of users to be added
        userList = [] # stores user names to be added
        passwdList = [] # stores passwords to be added
        encPasswdList = [] # stores the encrypted passwords to be added
        
        while True: # add users and passwords 
            userNo += 1 # count up number of users to be added
            
            while True: #input username
                print("\nUsername " + str(userNo))
                userName = input("[" + defaultUser + "] ? ")
                
                if not userName: # if no username given accept the default one
                    userName = defaultUser
                else:
                    defaultUser = userName
                    
                if userName in userList: # if the username is already given in this session
                    print("\nUsername already in list\nTry again")
                else:
                    userList.append(userName) # append username to list
                    break # break out of while loop
    
            while True: #input password
                print("\nPassword " + str(userNo))
                if show:
                    passwd1 = input("[" + defaultPasswd + "] ? ")
                else:
                    passwd1 = getpass("[" + defaultPasswd + "] ? ")
                
                if not passwd1: # if no password is given accept the default one
                    passwd1 = defaultPasswd
                    
                print("Enter password " + str(userNo) + " again")
                if show:
                    passwd2 = input("[" + defaultPasswd + "] ? ")
                else:
                    passwd2 = getpass("[" + defaultPasswd + "] ? ")
                
                if not passwd2: # if no password is given accept the default one
                    passwd2 = defaultPasswd
                    
                if passwd1 == passwd2: # check if the same password was given both times
                    passwdList.append(passwd1) # append password to list
                    break
                else:
                    print("\nPasswords do not match\nTry again")
                
            print ("\nDo you like to add another user") # add another user?
            addUser = input("(y/N) ? ")
            
            if addUser.lower() != "y": # if anything but 'y' was given
                break # break out of while loop
            else: # reset variables
                userName = ""
                passwd1 = ""
                passwd2 = ""
        
        # encrypt passwords
        if verbose:
            print("\n--- Encrypting passwords ...")
        for i in range(0, len(userList)):
            encPasswdList.append(f_key.encrypt(passwdList[i].encode())) # encrypt password and append to encrypted password as bytes

            
        # display all values and ask if correct
        print("\nNew connection:\n----------")
        print("IP:        " + ip)
        print("Host name: " + hostName)
        print("Port:      " + str(port))
        
        for i in range(0, len(userList)):
            if show:
                print("\nUser " + str(i + 1) + ": " + userList[i])
                print("Pass " + str(i + 1) + ": " + passwdList[i])
            else:
                print("\nUser " + str(i + 1) + ": " + userList[i])
                print("Pass " + str(i + 1) + ": " + str(encPasswdList[i].decode()))
        print("\nIs this correct")
        correct = input("(Y/n/q) ? ")
        
        if correct.lower() == "q": # if 'q' then exit
            print("\nExiting ...")
            sys.exit(0)
        elif correct.lower() != "n": # if anything but 'n' was stated
            break # break out of while loop
            
    if verbose:
        for i in range(0, len(userList)):
            enc = encPasswdList[i] # encrypted password
            print("\n--- Encrypted password " + str(i + 1) + ": " + str(enc))
            if show:
                dec = f_key.decrypt(enc) # decrypted password
                plain = bytes(dec).decode("utf-8") # plain text password
                print("--- Plain text password " + str(i + 1) + ": " + str(plain))
        
    print("\nAdding new connection ...") 
    
    writeConnection(connectionFile, ip, hostName, port, userList, encPasswdList, verbose)
    
def writeConnection(connectionFile, ip, hostName, port, userList, passwdList, verbose):    
    exUsers = 0
    
    config = configparser.ConfigParser()
    
    config.read(connectionFile)  # read config file

    if verbose:
        print("Adding " + str(len(userList)) + " users")

    try: # add section (IP)
        config.add_section(ip) # raises exception if ip already is a section
    except configparser.DuplicateSectionError:
        print("\nIP " + ip + " already exist")
    
    try: # add host name
        oldHostName = config.get(ip, 'hostname') # check if host name is present in section
    except:
        config[ip]['hostname'] = hostName # write host name to config
    else:
        print("Host name is already set to " + oldHostName)
        if oldHostName != hostName: # if new port differs from old
            print("Updating hostname with " + hostName)
            config.set(ip, 'hostname', hostName)
        
    try: # add port number
        oldPort = config.get(ip, 'port') # check if port is present in section
    except:
        config[ip]['port'] = str(port) # write port to config
    else:
        print("Port is already set to " + oldPort)
        if oldPort != str(port): # if new port differs from old
            print("Updating port with " + str(port))
            config.set(ip, 'port', str(port))
            
    options = config.options(ip) # load all options in section
    
    for option in options:
        if option.startswith('username'): # if option is username add one to existing users counter
            exUsers += 1

    if verbose:
        print("\n--- Users to add: " + str(len(userList)))
        print("    Existing users: " + str(exUsers))
              
    delUserList = []
    if verbose:
        print("\n--- Checking for existing entries ...")
    for i in range(0, len(userList)):            
        for ii in range(0, exUsers):
            oldUserName = config.get(ip, 'username' + str(ii))
            if verbose:
                print("    Checking new user: " + userList[i] + " with index: " + str(i))
                print("    against username" + str(ii) + ": " + oldUserName)
            if userList[i] == oldUserName:
                print("User " + userList[i] + " already exists")
                if verbose:
                    print("--- Will not add new user with index: " + str(i))
                delUserList.append(userList[i])
                
    if len(delUserList) >= 1:
        if verbose:
            print("\n--- Not adding " + str(len(delUserList)) + " out of " + str(len(userList)) + " indexes:")
        for delUser in delUserList:
            if verbose:
                delUserIndex = userList.index(delUser) 
                print("    Index: " + str(delUserIndex) + ", Username: " + userList[delUserIndex])
            userList.remove(delUser) # delete the username, with password, that was to be added
            passwdList.pop(delUserIndex)
        if verbose:
            print("    Users left to add: " + str(len(userList)))
            
                    
                  
                       

    print("\nThere was already " + str(exUsers) + " users for IP '" + ip + "'")
        
    if verbose:
        print("\n--- Adding connection ...")
        print("    IP:            " + ip)
        print("    Host name:     " + hostName)
        print("    Port:          " + str(port))    
    
    if len(userList) == 0:
        if verbose:
            print("\n--- No users was left to add")
    else:
        for i in range(0 + exUsers, len(userList) + exUsers): # start counting at number of existing users +1, count up to number of existing users + number of users to be added
            if verbose:
                print("\n    User " + str(i + 1) + ":     " + userList[i - exUsers])
                print("    Password " + str(i + 1) + ": " + str(passwdList[i - exUsers]))
            config[ip]['username' + str(i)] = userList[i - exUsers]
            passBytes = passwdList[i - exUsers]
            passString = passBytes.decode()
            config[ip]['password' + str(i)] = passString
    
    with open(connectionFile, 'w') as configfile:
        config.write(configfile)
        
    
    
    
    
    
    
    