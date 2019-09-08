#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, sys, socket

from makeConnection import selectConnection

from modules import decryptPassword, onError

def editConnections(f_key, connectionFile, show, verbose):
    print("\nEdit connection\n----------")
    
    if show:
        print("----------------------------------------------------")
    
    ip, host, port, userNo, userName, cryptPasswd = selectConnection(f_key, connectionFile, show, verbose)
    
    print("\nSelect what to edit:")
    print(" 1: IP:       " + ip)
    print(" 2: Hostname: " + host)
    print(" 3: Port    : " + port)
    print(" 4: Username: " + userName)
    if show:
        print(" 5: Password: " + decryptPassword(f_key, cryptPasswd, verbose))
    else:
        print(" 5: Password: *****")
        
    print("\nEnter number:")
    while True:
        selection = input(" ? ")
        
        if not selection:
            print("You must select a number 1-5\nTry again")
        else:
            try:
                selection = int(selection)
            except:
                print("Only integers allowed\nTry again:")
            else:
                if selection <= 0 or selection > 5:
                    print("Number must be 1-5")
                else:
                    break
                
    if selection == 1:
        changeSectionName(ip, connectionFile, show, verbose)
    elif selection == 2: # option, value, connectionFile, show, verbose
        changeValue(ip, "Hostname", host, connectionFile, show, verbose)
    elif selection == 3:
        changeValue(ip, "Port", port, connectionFile, show, verbose)
    elif selection == 4: # f_key, userNo, oldUserName, connectionFile, show, verbosee
        changeUsername(f_key, ip, userNo, userName, connectionFile, show, verbose)
    elif selection == 5:
        changeValue(f_key, ip, userNo, True, "Password", userName, cryptPasswd, connectionFile, show, verbose)
                
def updateConnection(ip, host, port, userName, plainTextPass, connectionFile, show, verbose):
    
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file
    
def changeSectionName(oldIP, connectionFile, show, verbose):
    if verbose:
        print("\n--- Changing name \n    on section [" + oldIP + "]")
    
    import ipaddress
    
    while True: # input ip
            print("\nEnter new IP")
            newIP = input("[" + oldIP + "] ? ")
            
            if not newIP or newIP == oldIP: # if no IP stated, accept default IP
                newIP = oldIP
                print("\nYou've entered the same IP again\nKeep old IP?")
                correct =input("(Y/n) ? ")
                if correct.lower() != "n": # if anything but 'n' was stated
                    print("\nKeeping old IP")
                    break
            else:
                if verbose:
                    print("--- Checking if IP is valid ...")
                    
                try:
                    ipaddress.ip_address(newIP) # raises an exception if IP is not correct
                except ValueError:
                    print("\n" + newIP + " is not a valid IP\nTry again")
                except:
                    print("\n" + newIP + " is a bad input\nTry again")
                else:
                    if verbose:
                        print("+++ Correct!")
                    break # break out of while loop
                
    if oldIP != newIP:
        print("\nChanging IP from " + oldIP + " to " + newIP)
        
        if verbose:
            print("\n--- Reading config file ...")
        config = configparser.ConfigParser()
        config.read(connectionFile)  # read config file
        
        if verbose:
            print("    Reading items from old section ...")      
        oldSectionItems = config.items(oldIP) # read items from section to rename
        if verbose:
            print("    Read " + str(len(oldSectionItems)) + " items")
        
        if verbose:
            print("    Adding new section ...")            
        config.add_section(newIP) # create section with the new name
        
        users = 0
        if verbose:
            print("    Writing old items to new section ...")  
        for option,value in oldSectionItems: # read old items
            if option.startswith("username"):
                users += 1
            config.set(newIP, option, value) # add old items to new section
        if verbose:
            print("    Added " + str(users) + " users")
        
        if verbose:
            print("    Deleting old section ...")  
        config.remove_section(oldIP) # delete old section
        
        if verbose:
            print("    Writing to config file ...")  
        with open(connectionFile, 'w') as configfile:
            config.write(configfile) # write everything to config file
    else:
        print("\nNo changes made")
    
def changeValue(ip, option, oldValue, connectionFile, show, verbose):    
    if verbose:
        print("\n--- Changing value for " + option.lower() + " \n    in section [" + ip + "]")
        
    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file
    
    print("\nOld " + option.lower() + ": " + oldValue)
    
    if option.lower() == "hostname":
        if verbose:
            print("\n--- Asking " + ip + " for hostname ...")
        try:
            hostName = socket.gethostbyaddr(ip)[0]
        except:
            hostName = ""
            onError(4, "Could not get hostname")
        else:
            if verbose:
                print("    OK\n    Got " + hostName)
            
        while True:  # input host name
            if hostName:
                print("\nHost name")
                newValue = input("[" + hostName + "] ? ")
                if not newValue: # if no value stated
                    newValue = hostName
            else:
                print("\nHost name")
                newValue = input("[" + oldValue + "] ? ")
                if not newValue:
                    newValue = oldValue
                    
            if newValue == oldValue:
                newValue = oldValue
                print("\nYou've entered the same " + option.lower() + " again\nKeep old " + option.lower() + "?")
                correct =input("(Y/n) ? ")
                if correct.lower() != "n": # if anything but 'n' was stated
                    print("\nKeeping old " + option.lower())
                    break
            else:
                if not newValue and not hostName: # if no host name stated and we could not probe a hostname
                    print("\nYou must state a hostname\nTry again")
                elif not newValue and hostName: # if no hostname stated and we could probe a hostname
                    newValue = hostName
                    break
                elif newValue:
                    break
                else:
                    newValue = oldValue
                    break # break out of while loop
            
    elif option.lower() == "port":
        while True: #input port
            print("\nRemote port")
            newValue = input("[" + oldValue + "] ? ")
            
            if not newValue: # if no port stated use old port
                newValue = oldValue
                
            if newValue == oldValue:
                newValue = oldValue
                print("\nYou've entered the same " + option.lower() + " again\nKeep old " + option.lower() + "?")
                correct =input("(Y/n) ? ")
                if correct.lower() != "n": # if anything but 'n' was stated
                    print("\nKeeping old " + option.lower())
                    break
            else:
                try:
                    newValue = int(newValue) # raises an exception if port is not an integer
                except:
                    print("\n" + str(newValue) + "is not an integer\nTry again")
                else:               
                    if verbose:
                        print("\n--- Checking if port is valid ...")
                    if newValue >= 0 and newValue <= 65535: # port must be between 0 and 65535
                        if verbose:
                            print("    OK")
                        newValue = str(newValue)
                        break # break out of while loop
                    else:
                        print("\n" + str(newValue) + " is outside the range 0-65535\nTry again")
                    
    
    if oldValue != newValue:
        print("\nChanging " + option.lower() + " from " + oldValue + " to " + newValue)
        if verbose:
            print("\n--- Writing new value ...")
        config.set(ip, option, newValue)
        if verbose:
            print("    Writing to config file ...")  
        with open(connectionFile, 'w') as configfile:
            config.write(configfile) # write everything to config file
    else:
        print("\nNo changes made")
    
def changeUsername(f_key, ip, userNo, oldUsername, connectionFile, show, verbose):    
    if verbose:
        print("\n--- Changing username for username" + str(userNo) + " \n    in section [" + ip + "]")
        
    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file
    
    print("\nOld username: " + oldUsername)
    
    #if show:
    #    print("\nOld password: " + decryptPassword(f_key, value, verbose))
    #else:
    #    print("\nOld password: *****")
   
    
    
    
    
    
            
            
        
    
    
    
    