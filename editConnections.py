#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, sys

from makeConnection import selectConnection

def editConnections(f_key, connectionFile, show, verbose):
    print("\nEdit connection\n----------")
    
    if show:
        print("----------------------------------------------------")
    
    ip, host, port, userName, plainTextPass = selectConnection(f_key, connectionFile, show, verbose)
    
    print("\nSelect what to edit:")
    print(" 1: IP:       " + ip)
    print(" 2: Hostname: " + host)
    print(" 3: Port    : " + port)
    print(" 4: Username: " + userName)
    if show:
        print(" 5: Password: " + plainTextPass)
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
                
def updateConnection(ip, host, port, userName, plainTextPass, connectionFile, show, verbose):
    
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file
    
def changeSectionName(oldIP, connectionFile, show, verbose):
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
                    sys.exit(0)
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
    
    
    
    
    
    