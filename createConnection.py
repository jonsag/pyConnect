#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import sys, ipaddress, configparser, socket

from getpass import getuser, getpass

#from cryptography.fernet import Fernet

from modules import get_ip, onError, encryptPassword, decryptPassword

def createConnection(f_key, connectionFile, show, verbose):
    print("\nCreate new connection\n----------")
    
    defaultIP = get_ip() # this computers IP
    hostName = ""
    defaultPort = "22"
    defaultUser = getuser() # user running this script
    defaultPasswd = "xxxxx"
    
    while True: # run until all users are added
        while True: # input ip
            print("\nRemote IP")
            ip = input("[" + defaultIP + "] ? ")
            
            if not ip: # if no IP stated, accept default IP
                ip = defaultIP
            
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
                    print("    OK")
                break # break out of while loop
             
        if verbose:
            print("\n--- Asking " + ip + " for hostname ...")
        try:
            hostName = socket.gethostbyaddr(ip)[0] # probe for hostname
        except:
            hostName = ""
            onError(4, "Could not get hostname")
        else:
            if verbose:
                print("    OK\n    Got " + hostName)
            
        while True:  # input host name
            if hostName: # if hostname could be probed
                print("\nHost name")
                newHostName = input("[" + hostName + "] ? ")
            else:
                print("\nHost name")
                newHostName = input(" ? ")
            
            if not newHostName and not hostName: # if no hostname stated and no hostname could be probed
                print("\nYou must state a hostname\nTry again")
            elif not newHostName and hostName: # if no hostname stated but hostname was probed
                break
            else:
                hostName = newHostName
                break # break out of while loop
                
        while True: #input port
            print("\nRemote port")
            port = input("[" + defaultPort + "] ? ")
            
            if not port: # if no port stated use default port
                port = defaultPort
            
            try:
                port = int(port) # raises an exception if port is not an integer
            except:
                print("\n" + str(port) + "is not an integer\nTry again")
            else:                
                if verbose:
                    print("\n--- Checking if port is valid ...")
                if port >= 0 and port <= 65535: # port must be between 0 and 65535
                    if verbose:
                        print("    OK")
                    break # break out of while loop
                else:
                    print("\n" + str(port) + " is outside the range 0-65535\nTry again")
        
        userNo = 0 # stores number of users to be added
        userList = [] # stores user names to be added
        passwdList = [] # stores passwords to be added
        cryptPasswdList = [] # stores the encrypted passwords to be added
        
        while True: # add users and passwords 
            userNo += 1 # count up number of users to be added
            
            while True: #input username
                print("\nUsername " + str(userNo))
                username = input("[" + defaultUser + "] ? ")
                
                if not username: # if no username given accept the default one
                    username = defaultUser
                else:
                    defaultUser = username
                    
                if username in userList: # if the username is already given in this session
                    print("\nUsername already in list\nTry again")
                else:
                    userList.append(username) # append username to list
                    break # break out of while loop
    
            while True: #input password
                print("\nPassword " + str(userNo))
                if show:
                    passwd1 = input("[" + defaultPasswd + "] ? ") # enter password invisible
                else:
                    passwd1 = getpass("[" + defaultPasswd + "] ? ") # enter password visibly
                
                if not passwd1: # if no password is given accept the default one
                    passwd1 = defaultPasswd
                    
                print("Enter password " + str(userNo) + " again")
                if show:
                    passwd2 = input("[" + defaultPasswd + "] ? ") # enter password invisible
                else:
                    passwd2 = getpass("[" + defaultPasswd + "] ? ") # enter password visibly
                
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
                username = ""
                passwd1 = ""
                passwd2 = ""
        
        # encrypt passwords
        if verbose:
            print("\n--- Encrypting passwords ...")
        for i in range(0, len(userList)):
            cryptPasswdList.append(encryptPassword(f_key, passwdList[i], show, verbose))
            #cryptPasswdList.append(f_key.encrypt(passwdList[i].encode())) # encrypt password and append to encrypted password as bytes

            
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
                print("Pass " + str(i + 1) + ": " + cryptPasswdList[i])
                
        print("\nIs this correct")
        correct = input("(Y/n/q) ? ")
        
        if correct.lower() == "q": # if 'q' then exit
            print("\nExiting ...")
            sys.exit(0)
        elif correct.lower() != "n": # if anything but 'n' was stated
            break # break out of while loop
            
    if verbose:
        for i in range(0, len(userList)):
            cryptPasswd = cryptPasswdList[i] # encrypted password
            print("\n--- Encrypted password " + str(i + 1) + ": " + cryptPasswd)
            if show:
                print("\n--- Plain text password " + str(i + 1) + ": " + decryptPassword(f_key, cryptPasswd, verbose))
                #dec = f_key.decrypt(enc) # decrypted password
                #plain = bytes(dec).decode("utf-8") # plain text password
                #print("--- Plain text password " + str(i + 1) + ": " + str(plain))
        
    print("\nAdding new connection ...") 
    
    writeConnections(f_key, connectionFile, ip, hostName, port, userList, cryptPasswdList, show, verbose)
    
def writeConnections(f_key, connectionFile, ip, hostName, port, userList, cryptPasswdList, show, verbose):    
    exUsers = 0
    
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file

    if verbose:
        print("Adding " + str(len(userList)) + " users")

    try: # add section [IP]
        config.add_section(ip) # raises exception if ip already is a section
    except configparser.DuplicateSectionError:
        print("\nIP " + ip + " already exist")
    
    try: # add host name
        oldHostName = config.get(ip, 'hostname') # check if host name is present in section
    except:
        config[ip]['hostname'] = hostName # write host name to config
    else:
        if oldHostName == hostName:
            print("Host name is already set to " + oldHostName)
        else: # if new port differs from old
            print("Updating hostname from " + oldHostName + " with " + hostName)
        
    try: # add port number
        oldPort = config.get(ip, 'port') # check if port is present in section
    except:
        config[ip]['port'] = str(port) # write port to config
    else:
        if oldPort == str(port):
            print("Port is already set to " + oldPort)
        else: # if new port differs from old
            print("Updating port from " + oldPort + " with " + str(port))
            
    options = config.options(ip) # load all options in section
    
    for option in options:
        if option.startswith('username'): # if option is username add one to existing users counter
            exUsers += 1

    if verbose:
        print("\n--- Users to add: " + str(len(userList)))
        print("    Existing users: " + str(exUsers))
    else:
        if exUsers >= 1:
            print("\nThere was already " + str(exUsers) + " users for IP '" + ip + "'")
        
    delUserList = [] # will contain usernames that exist both in section and in the add-list 
    if verbose:
        print("\n--- Checking for existing entries ...")
    for i in range(0, len(userList)): # count up to number if users that is to be added
        for ii in range(0, exUsers): # count up to number of users already in this section
            oldUsername = config.get(ip, 'username' + str(ii)) # username for 'username#'
            if verbose:
                print("    Checking new user: " + userList[i] + " with index: " + str(i) + 
                      ", against username" + str(ii) + ": " + oldUsername)
            if userList[i] == oldUsername:
                print("User " + userList[i] + " already exists")
                if verbose:
                    print("--- Will not add new user with index: " + str(i))
                delUserList.append(userList[i])
                
    if len(delUserList) >= 1:
        if verbose:
            print("\n--- Not adding " + str(len(delUserList)) + " out of " + str(len(userList)) + " indexes:")
        for delUser in delUserList:
            if verbose:
                delUserIndex = userList.index(delUser) #  get the index-number for username in add-list
                print("    Index: " + str(delUserIndex) + ", Username: " + userList[delUserIndex])
            userList.remove(delUser) # delete the username from add-list
            cryptPasswdList.pop(delUserIndex) # delete the password with that index-number
        if verbose:
            print("    Users left to add: " + str(len(userList)))
        
    if verbose:
        print("\n--- Adding connection ...")
        print("    IP:            " + ip)
        print("    Host name:     " + hostName)
    config.set(ip, 'hostname', hostName)
    if verbose:
        print("    Port:          " + str(port))    
    config.set(ip, 'port', str(port))
    
    if len(userList) == 0:
        if verbose:
            print("\n--- No users was left to add")
    else:
        for i in range(0 + exUsers, len(userList) + exUsers): # start counting at number of existing users +1, count up to number of existing users + number of users to be added
            if verbose:
                print("\n    User " + str(i + 1) + ":     " + userList[i - exUsers])            
            config[ip]['username' + str(i)] = userList[i - exUsers]
            
            #passBytes = cryptPasswdList[i - exUsers]
            #passString = passBytes.decode()
            #config[ip]['password' + str(i)] = passString
            if verbose:
                if show:
                    print("    Password " + str(i + 1) + ": " + decryptPassword(f_key, cryptPasswdList[i - exUsers], verbose))
                else:
                    print("    Password " + str(i + 1) + ": " + cryptPasswdList[i - exUsers])
                
                    
            config[ip]['password' + str(i)] = cryptPasswdList[i - exUsers]
    
    with open(connectionFile, 'w') as configfile:
        config.write(configfile)
        
    
    
    
    
    
    
    