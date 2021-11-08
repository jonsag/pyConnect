#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import configparser, socket

from makeConnection import selectConnection

from modules import decryptPassword, onError, encryptPassword


def editConnections(f_key, connectionFile, show, verbose):
    print("\nEdit connection\n----------")

    if show:
        print("----------------------------------------------------")

    ip, host, port, userNo, username, cryptPasswd = selectConnection(
        f_key, connectionFile, show, verbose
    )

    maxNumber = 5

    print("\nSelect what to edit:")
    print(" 1: IP:       " + ip)
    print(" 2: Hostname: " + host)
    print(" 3: Port    : " + port)
    if userNo >= 0:
        print(" 4: Username: " + username)
        if show:
            print(" 5: Password: " + decryptPassword(f_key, cryptPasswd, verbose))
        else:
            print(" 5: Password: *****")
    else:
        maxNumber = 3

    print("\nEnter number:")
    while True:
        selection = input(" ? ")

        if not selection:
            print("\nYou must select a number 1-" + str(maxNumber) + "\nTry again")
        else:
            try:
                selection = int(selection)
            except:
                print("Only integers allowed\nTry again:")
            else:
                if selection <= 0 or selection > maxNumber:
                    print("Number must be 1-" + str(maxNumber))
                else:
                    break

    if selection == 1:
        changeSectionName(ip, host, connectionFile, show, verbose)
    elif selection == 2:  # option, value, connectionFile, show, verbose
        changeValue(ip, "Hostname", host, connectionFile, show, verbose)
    elif selection == 3:
        changeValue(ip, "Port", port, connectionFile, show, verbose)
    elif selection == 4:  # f_key, userNo, oldUsername, connectionFile, show, verbosee
        changeUsername(
            f_key, ip, userNo, username, cryptPasswd, connectionFile, show, verbose
        )
    elif selection == 5:
        changePassword(f_key, ip, userNo, cryptPasswd, connectionFile, show, verbose)


def changeSectionName(oldIP, host, connectionFile, show, verbose):
    if verbose:
        print("\n--- Changing name \n    on section [" + oldIP + "]")

    import ipaddress

    deleteSection = False

    while True:  # input ip
        print("\nEnter new IP, or 'd' to delete")
        newIP = input("[" + oldIP + "]/d ? ")

        if newIP.lower() == "d":
            deleteSection = True
            break

        if not newIP or newIP == oldIP:  # if no IP stated, accept default IP
            newIP = oldIP
            print("\nYou've entered the same IP again\nKeep old IP?")
            correct = input("(Y/n) ? ")
            if correct.lower() != "n":  # if anything but 'n' was stated
                print("\nKeeping old IP")
                break
        else:
            if verbose:
                print("--- Checking if IP is valid ...")

            try:
                ipaddress.ip_address(newIP)  # raises an exception if IP is not correct
            except ValueError:
                print("\n" + newIP + " is not a valid IP\nTry again")
            except:
                print("\n" + newIP + " is a bad input\nTry again")
            else:
                if verbose:
                    print("+++ Correct!")
                break  # break out of while loop

    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file

    if not deleteSection:
        if oldIP != newIP:
            print("\nChanging IP from " + oldIP + " to " + newIP)

            if verbose:
                print("    Reading items from old section ...")
            oldSectionItems = config.items(oldIP)  # read items from section to rename
            if verbose:
                print("    Read " + str(len(oldSectionItems)) + " items")

            if verbose:
                print("    Adding new section ...")
            config.add_section(newIP)  # create section with the new name

            users = 0
            if verbose:
                print("    Writing old items to new section ...")
            for option, value in oldSectionItems:  # read old items
                if option.startswith("username"):
                    users += 1
                config.set(newIP, option, value)  # add old items to new section
            if verbose:
                print("    Added " + str(users) + " users")

            if verbose:
                print("    Deleting old section ...")
            config.remove_section(oldIP)  # delete old section
        else:
            print("\nNo changes made")
    else:  # delete section
        print("\nAre you sure you want to delete connection for " + oldIP + ", ", host)
        delete = input("(y/N) ? ")

        if delete.lower() == "y":
            print("\nDeleting connection for IP " + oldIP)
            config.remove_section(oldIP)  # delete section
        else:
            print("\nNo changes made")

    if verbose:
        print("\n--- Writing to config file ...")
    with open(connectionFile, "w") as configfile:
        config.write(configfile)  # write everything to config file


def changeValue(ip, option, oldValue, connectionFile, show, verbose):
    if verbose:
        print(
            "\n--- Changing value for "
            + option.lower()
            + " \n    in section ["
            + ip
            + "]"
        )

    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file

    print("\nOld " + option.lower() + ": " + oldValue)

    if option.lower() == "hostname":
        if verbose:
            print("\n--- Asking " + ip + " for hostname ...")
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = ""
            onError(4, "Could not get hostname")
        else:
            if verbose:
                print("    OK\n    Got " + hostname)

        while True:  # input host name
            if hostname:
                print("\nHost name")
                newValue = input("[" + hostname + "] ? ")
                if not newValue:  # if no value stated
                    newValue = hostname
            else:
                print("\nHost name")
                newValue = input("[" + oldValue + "] ? ")
                if not newValue:
                    newValue = oldValue

            if newValue == oldValue:
                newValue = oldValue
                print(
                    "\nYou've entered the same "
                    + option.lower()
                    + " again\nKeep old "
                    + option.lower()
                    + "?"
                )
                correct = input("(Y/n) ? ")
                if correct.lower() != "n":  # if anything but 'n' was stated
                    print("\nKeeping old " + option.lower())
                    break
            else:
                if (
                    not newValue and not hostname
                ):  # if no host name stated and we could not probe a hostname
                    print("\nYou must state a hostname\nTry again")
                elif (
                    not newValue and hostname
                ):  # if no hostname stated and we could probe a hostname
                    newValue = hostname
                    break
                elif newValue:
                    break
                else:
                    newValue = oldValue
                    break  # break out of while loop

    elif option.lower() == "port":
        while True:  # input port
            print("\nRemote port")
            newValue = input("[" + oldValue + "] ? ")

            if not newValue:  # if no port stated use old port
                newValue = oldValue

            if newValue == oldValue:
                newValue = oldValue
                print(
                    "\nYou've entered the same "
                    + option.lower()
                    + " again\nKeep old "
                    + option.lower()
                    + "?"
                )
                correct = input("(Y/n) ? ")
                if correct.lower() != "n":  # if anything but 'n' was stated
                    print("\nKeeping old " + option.lower())
                    break
            else:
                try:
                    newValue = int(
                        newValue
                    )  # raises an exception if port is not an integer
                except:
                    print("\n" + str(newValue) + "is not an integer\nTry again")
                else:
                    if verbose:
                        print("\n--- Checking if port is valid ...")
                    if (
                        newValue >= 0 and newValue <= 65535
                    ):  # port must be between 0 and 65535
                        if verbose:
                            print("    OK")
                        newValue = str(newValue)
                        break  # break out of while loop
                    else:
                        print(
                            "\n"
                            + str(newValue)
                            + " is outside the range 0-65535\nTry again"
                        )

    if oldValue != newValue:
        print("\nChanging " + option.lower() + " from " + oldValue + " to " + newValue)
        if verbose:
            print("\n--- Writing new value ...")
        config.set(ip, option, newValue)
        if verbose:
            print("    Writing to config file ...")
        with open(connectionFile, "w") as configfile:
            config.write(configfile)  # write everything to config file
    else:
        print("\nNo changes made")


def changeUsername(
    f_key, ip, userNo, oldUsername, oldCryptPasswd, connectionFile, show, verbose
):
    if verbose:
        print(
            "\n--- Changing username for username"
            + str(userNo)
            + " \n    in section ["
            + ip
            + "]"
        )

    print("\nOld username: " + oldUsername)

    deleteUser = False

    while True:  # input username
        print("\nEnter new username, or 'd' to delete")
        newUsername = input("[" + oldUsername + "]/d ? ")

        if newUsername.lower() == "d":
            deleteUser = True
            break

        if (
            not newUsername or newUsername == oldUsername
        ):  # if no username stated, accept old username
            newUsername = oldUsername
            print("\nYou've entered the same username again\nKeep old username?")
            correct = input("(Y/n) ? ")
            if correct.lower() != "n":  # if anything but 'n' was stated
                print("\nKeeping old username")
                break
        else:
            break

    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file

    if not deleteUser:
        changedUsername = False
        if oldUsername != newUsername:
            print(
                "\nChanging username from "
                + oldUsername
                + " to "
                + newUsername
                + " ..."
            )
            if verbose:
                print("\n--- Writing new username ...")
            config.set(ip, "username" + str(userNo), newUsername)
            changedUsername = True
        else:
            print("\nNo changes made")

    else:  # delete user
        print("\nAre you sure you want to delete user " + oldUsername)
        delete = input("(y/N) ? ")

        if delete.lower() == "y":
            print("\nDeleting user " + oldUsername + " with password")
            config.remove_option(ip, "username" + str(userNo))  # delete user and pass
            config.remove_option(ip, "password" + str(userNo))

            # move the last user (if there is one) to the now empty username#
            remainUsers = 0
            options = config.options(ip)
            for option in options:
                if option.startswith("username"):
                    remainUsers += 1
            if verbose:
                print("\n--- " + str(remainUsers) + " users now remains")
            if (
                remainUsers >= 1 and remainUsers != userNo
            ):  # if there are more than one users remaining and it wasn't the last user we deleted
                if verbose:
                    print(
                        "\n--- Getting username and password for user "
                        + str(remainUsers)
                    )
                oldUser = config.get(
                    ip, "username" + str(remainUsers)
                )  # read old user and pass
                oldPasswd = config.get(ip, "password" + str(remainUsers))
                if verbose:
                    print("\n--- Moving user " + oldUser)
                    if show:
                        print(
                            "    with password "
                            + decryptPassword(f_key, oldPasswd, verbose)
                        )
                    else:
                        print("    with password " + oldPasswd)
                config.remove_option(
                    ip, "username" + str(remainUsers)
                )  # delete old user and pass
                config.remove_option(ip, "password" + str(remainUsers))
                config.set(
                    ip, ("username" + str(userNo)), oldUser
                )  # rewrite old user and pass
                config.set(ip, ("password" + str(userNo)), oldPasswd)

            if verbose:
                print("\n--- Writing to config file ...")
            with open(connectionFile, "w") as configfile:
                config.write(configfile)  # write everything to config file
            changedUsername = False
        else:
            print("\nNo changes made")

    if verbose:
        print("\n--- Writing to config file ...")
    with open(connectionFile, "w") as configfile:
        config.write(configfile)  # write everything to config file

    if changedUsername:
        print("\nWould you also like to change the password")
        changePasswd = input("(y/N) ? ")

        if changePasswd.lower() == "y":
            changePassword(
                f_key, ip, userNo, oldCryptPasswd, connectionFile, show, verbose
            )


def changePassword(f_key, ip, userNo, oldCryptPasswd, connectionFile, show, verbose):
    from getpass import getpass

    if verbose:
        print(
            "\n--- Changing password for password"
            + str(userNo)
            + " \n    in section ["
            + ip
            + "]"
        )

    oldPlainTextPasswd = decryptPassword(f_key, oldCryptPasswd, verbose)

    if show:
        print("\nOld password: " + oldPlainTextPasswd)
    else:
        print("\nOld passwd: *****")

    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config fil

    while True:  # input password
        print("\nPassword ")
        if show:
            passwd1 = input(
                "[" + decryptPassword(f_key, oldCryptPasswd, verbose) + "] ? "
            )  # enter password invisible
        else:
            passwd1 = getpass("[*****] ? ")  # enter password visibly

        if not passwd1:  # if no password is given accept the default one
            passwd1 = decryptPassword(f_key, oldCryptPasswd, verbose)

        print("\nEnter password again")
        if show:
            passwd2 = input(
                "[" + decryptPassword(f_key, oldCryptPasswd, verbose) + "] ? "
            )  # enter password invisible
        else:
            passwd2 = getpass("[*****] ? ")  # enter password visibly

        if not passwd2:  # if no password is given accept the default one
            passwd2 = decryptPassword(f_key, oldCryptPasswd, verbose)

        if passwd1 == passwd2:  # check if the same password was given both times
            break
        else:
            print("\nPasswords do not match\nTry again")

    if oldPlainTextPasswd != passwd1:
        if show:
            print(
                "\nChanging password from "
                + oldPlainTextPasswd
                + " to "
                + passwd1
                + " ..."
            )
        else:
            print("\nChanging password ...")
        newEncPasswd = encryptPassword(f_key, passwd1, show, verbose)
        if verbose:
            print("\n--- Writing new passwd ...")
        config.set(ip, "password" + str(userNo), newEncPasswd)
    else:
        if passwd1:
            print("\nYou have entered the old password again")
        print("\nNo changes made")

    if verbose:
        print("\n--- Writing to config file ...")
    with open(connectionFile, "w") as configfile:
        config.write(configfile)  # write everything to config file
