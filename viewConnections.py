#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser

from modules import decryptPassword

def viewConnections(f_key, connectionFile, show, verbose):
    connectionNo = 0
    
    #ciphered_text = f_key.encrypt(b"SuperSecretPassword")   #required to be bytes
    #print("\nEncrypted text: " + str(ciphered_text))
    
    #unciphered_text = (f_key.decrypt(ciphered_text))
    #print("\nDecrypted text: " + str(unciphered_text))
    
    #plain_text_encryptedpassword = bytes(unciphered_text).decode("utf-8") #convert to string
    #print("\nPlain text password: " + plain_text_encryptedpassword)
    
    config = configparser.ConfigParser()
    
    config.read(connectionFile)  # read config file
    
    sections = config.sections()
    
    for section in sections:
        connectionNo += 1
        print("\nConnection " + str(connectionNo) + "\n----------")
        print(section)
        
        print("    Port:     " + config.get(section, 'port'))
        
        print("    Hostname: " + config.get(section, 'hostname'))
        
        options = config.options(section)
        
        for option in options:
            if option.startswith('username'):
                print("\n    User:     " + config.get(section, option))
            elif option.startswith('password'):
                
                cryptPasswd = config.get(section, option)
                if show:
                    plainTextPass = decryptPassword(f_key, cryptPasswd, verbose)
                    print("    Pass:     " + plainTextPass)
                else:
                    print("    Pass:     " + cryptPasswd)
                    
    print()
                    
                #encryptedPassword = config.get(section, option)
                #encryptedPassword = encryptedPassword.encode()
                #decryptedPassword = f_key.decrypt(encryptedPassword)               
                #plainTextPassword = bytes(decryptedPassword).decode("utf-8")
                
                
                
                
                
                
                
                
                
                
                
                