#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import sys, configparser, socket, validators

from getpass import getuser, getpass

# from cryptography.fernet import Fernet

from modules import get_ip, onError, encryptPassword, decryptPassword


def createConnection(f_key, connectionFile, show, verbose):
    print("\nCreate new connection\n----------")

    defaultIP = get_ip()  # this computers IP
    hostname = ""
    defaultPort = "22"
    defaultUser = getuser()  # user running this script
    defaultPasswd = "xxxxx"

    newSection = False
    sectionNo = 1

    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file

    oldSections = config.sections()

    print("\n1: Add new")

    for oldIP in oldSections:
        sectionNo += 1
        oldPort = config.get(oldIP, "port")
        oldHostname = config.get(oldIP, "hostname")
        print(str(sectionNo) + ": " + oldIP + ", " + oldHostname)

    print("\nEnter number:")
    while True:
        selection = input("(1) ? ")

        if not selection:
            selection = 1
            break
        else:
            try:
                selection = int(selection)
            except:
                print("\nOnly integers allowed\nTry again:")
            else:
                if selection <= 0 or selection > sectionNo:
                    print("Number must be 1-" + str(sectionNo))
                else:
                    break

    if selection == 1:
        newSection = True
    else:
        ip = oldIP
        hostname = oldHostname
        port = oldPort
        print("\nHostname: " + hostname)
        print("Port:     " + str(port))

    while True:  # section loop, run until all users are added
        if newSection:  # if select new section, continue here
            while True:  # ip loop, run until all users are added
                print("\nRemote IP")
                ip = input("[" + defaultIP + "] ? ")

                if not ip:  # if no IP stated, accept default IP
                    ip = defaultIP

                ipValid = False
                isURL = False

                if verbose:
                    print("\n--- Checking if " + ip + " is a valid IPv4 ...")
                if not validators.ip_address.ipv4(ip):
                    if verbose:
                        print("    Not a valid IPv4")
                else:
                    if verbose:
                        print("    OK\n    Is a valid IPv4")
                    ipValid = True

                if not ipValid:
                    if verbose:
                        print("\n--- Checking if " + ip + " is a valid IPv6 ...")
                    if not validators.ip_address.ipv6(ip):
                        if verbose:
                            print("    Not a valid IPv6")
                    else:
                        if verbose:
                            print("    OK\n    Is a valid IPv6")
                        ipValid = True

                if not ipValid:
                    if verbose:
                        print("\n--- Checking if " + ip + " is a valid domain ...")
                    if not validators.domain(ip):
                        if verbose:
                            print("    Not a domain")
                    else:
                        if verbose:
                            print("    OK\n    Is a valid domain")
                        isURL = True
                        ipValid = True

                if not ipValid:
                    if verbose:
                        print("\n--- Checking if " + ip + " is a valid URL ...")
                    if not validators.url("http://" + ip):
                        if verbose:
                            print("    Not a URL")
                    else:
                        if verbose:
                            print("    OK\n    Is a valid URL")
                        isURL = True
                        ipValid = True

                if ipValid:
                    if verbose:
                        print("\n--- Checking if " + ip + " is already in sections ...")
                    for existingIP in oldSections:
                        if existingIP == ip:
                            if verbose:
                                print("    Found matching ip")
                            else:
                                print(
                                    "\n"
                                    + ip
                                    + " is already added\nUsing old hostname and port"
                                )
                            oldPort = config.get(oldIP, "port")
                            oldHostname = config.get(oldIP, "hostname")
                            if verbose:
                                print(
                                    "    Using old hostname "
                                    + oldHostname
                                    + " and port "
                                    + oldPort
                                )
                            newSection = False
                    break  # break out of  ip loop
                else:
                    print(
                        "\n"
                        + ip
                        + "is not\n    a valid IPv4 address,\n    a valid IPv6 address,\n    a valid domain name,\n    a valid URL"
                    )
                    print("Try again")

            if verbose:
                print("\n--- Asking " + ip + " for hostname ...")
            if isURL:
                if verbose:
                    print("\n--- Trying to resolve " + ip + " ...")
                try:
                    domain, data, domainIP = socket.gethostbyname_ex(ip)
                except:
                    print("\nCould not get hostname")
                else:
                    probeIP = domainIP[0]
                    if verbose:
                        print("    OK\n    Got IP " + probeIP)
            else:
                probeIP = ip

            try:
                hostname = socket.gethostbyaddr(probeIP)[0]  # probe for hostname
            except:
                hostname = ""
                onError(4, "Could not get hostname")
            else:
                if verbose:
                    print("    OK\n    Got " + hostname)

        if newSection:
            while True:  # hostname loop, input host name
                if hostname:  # if hostname could be probed
                    print("\nHost name")
                    newHostname = input("[" + hostname + "] ? ")
                else:
                    print("\nHost name")
                    newHostname = input(" ? ")

                if (
                    not newHostname and not hostname
                ):  # if no hostname stated and no hostname could be probed
                    print("\nYou must state a hostname\nTry again")
                elif (
                    not newHostname and hostname
                ):  # if no hostname stated but hostname was probed
                    break
                else:
                    hostname = newHostname
                    break  # break out of hostname loop

        if newSection:
            while True:  # port loop, input port
                print("\nRemote port")
                port = input("[" + defaultPort + "] ? ")

                if not port:  # if no port stated use default port
                    port = defaultPort

                try:
                    port = int(port)  # raises an exception if port is not an integer
                except:
                    print("\n" + str(port) + "is not an integer\nTry again")
                else:
                    if verbose:
                        print("\n--- Checking if port is valid ...")
                    if port >= 0 and port <= 65535:  # port must be between 0 and 65535
                        if verbose:
                            print("    OK")
                        break  # break out of port loop
                    else:
                        print(
                            "\n"
                            + str(port)
                            + " is outside the range 0-65535\nTry again"
                        )

        userNo = 0  # stores number of users to be added
        userList = []  # stores user names to be added
        passwdList = []  # stores passwords to be added
        cryptPasswdList = []  # stores the encrypted passwords to be added

        while True:  # user-pass loop, add users and passwords
            userNo += 1  # count up number of users to be added

            jumpToAdd = False

            while True:  # username loop, input username
                print("\nUsername " + str(userNo))
                username = input("(" + defaultUser + ")/q ? ")

                if not username:  # if no username given accept the default one
                    username = defaultUser
                elif username.lower() == "q":
                    jumpToAdd = True
                    break  # break out of username loop
                else:
                    defaultUser = username

                isNewUser = True

                if verbose:
                    print(
                        "\n--- Checking if " + username + " is already in add-list ..."
                    )
                if (
                    username in userList
                ):  # if the username is already given in this session
                    isNewUser = False
                    print("\nUsername already in list\nTry again")
                else:
                    if verbose:
                        print("    OK\n    User not in list")

                    if verbose:
                        print(
                            "\n--- Checking if "
                            + username
                            + " is already in connections ..."
                        )
                        print("    Trying to read usernames from connections")
                    try:
                        options = config.options(ip)
                    except:
                        if verbose:
                            print("    No section for ip " + ip)
                        # break # this username not added in this session and ip not in connections
                    else:
                        for option in options:
                            if option.startswith("username"):
                                if config.get(ip, option) == username:
                                    isNewUser = False
                                    if verbose:
                                        print(
                                            "    Username "
                                            + username
                                            + " already in connections"
                                        )
                                else:
                                    if verbose:
                                        print("    No matches found in connections")

                if isNewUser:
                    if verbose:
                        print("    Adding " + username + " to add-list")
                    userList.append(username)  # append username to list
                    break  # break out of while loop
                else:
                    print("\nUsername already exists for this IP\nTry again")

            if jumpToAdd:
                break  # break out of user-pass loop
            else:
                while True:  # password loop, input password
                    print("\nPassword " + str(userNo))
                    if show:
                        passwd1 = input(
                            "[" + defaultPasswd + "] ? "
                        )  # enter password invisible
                    else:
                        passwd1 = getpass(
                            "[" + defaultPasswd + "] ? "
                        )  # enter password visibly

                    if not passwd1:  # if no password is given accept the default one
                        passwd1 = defaultPasswd

                    print("\nEnter password " + str(userNo) + " again")
                    if show:
                        passwd2 = input(
                            "[" + defaultPasswd + "] ? "
                        )  # enter password invisible
                    else:
                        passwd2 = getpass(
                            "[" + defaultPasswd + "] ? "
                        )  # enter password visibly

                    if not passwd2:  # if no password is given accept the default one
                        passwd2 = defaultPasswd

                    if (
                        passwd1 == passwd2
                    ):  # check if the same password was given both times
                        passwdList.append(passwd1)  # append password to list
                        break  # break out of password loop
                    else:
                        print("\nPasswords do not match\nTry again")

            print("\nDo you like to add another user")  # add another user?
            addUser = input("(y/N) ? ")

            if addUser.lower() != "y":  # if anything but 'y' was given
                break  # break out of user-pass loop
            else:  # reset variables
                username = ""
                passwd1 = ""
                passwd2 = ""

        if newSection or len(userList) >= 1:
            # encrypt passwords
            if verbose:
                print("\n--- Encrypting passwords ...")
            for i in range(0, len(userList)):
                cryptPasswdList.append(
                    encryptPassword(f_key, passwdList[i], show, verbose)
                )
                # cryptPasswdList.append(f_key.encrypt(passwdList[i].encode())) # encrypt password and append to encrypted password as bytes

            # display all values and ask if correct
            print("\nNew connection:\n----------")
            print("IP:        " + ip)
            print("Host name: " + hostname)
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

            if correct.lower() == "q":  # if 'q' then exit
                print("\nExiting ...")
                sys.exit(0)
            elif correct.lower() == "n":  # if anything but 'n' was stated
                break  # break out of  loop
            else:
                for i in range(0, len(userList)):  # encrypt passwords
                    cryptPasswd = cryptPasswdList[i]  # encrypted password
                    if verbose:
                        print(
                            "\n--- Encrypted password "
                            + str(i + 1)
                            + ": "
                            + cryptPasswd
                        )
                        if show:
                            print(
                                "\n--- Plain text password "
                                + str(i + 1)
                                + ": "
                                + decryptPassword(f_key, cryptPasswd, verbose)
                            )

                print("\nAdding new connection ...")

                writeConnections(
                    f_key,
                    connectionFile,
                    ip,
                    hostname,
                    port,
                    userList,
                    cryptPasswdList,
                    show,
                    verbose,
                )
                break
        else:
            print("\nNothing to add\n\nNo changes made")
            break  # break out of section loop


def writeConnections(
    f_key, connectionFile, ip, hostname, port, userList, cryptPasswdList, show, verbose
):
    exUsers = 0

    if verbose:
        print("\n--- Reading config file ...")
    config = configparser.ConfigParser()
    config.read(connectionFile)  # read config file

    if verbose:
        print("Adding " + str(len(userList)) + " users")

    try:  # add section [IP]
        config.add_section(ip)  # raises exception if ip already is a section
    except configparser.DuplicateSectionError:
        print("\nIP " + ip + " already exist")

    try:  # add host name
        oldHostname = config.get(
            ip, "hostname"
        )  # check if host name is present in section
    except:
        config[ip]["hostname"] = hostname  # write host name to config
    else:
        if oldHostname == hostname:
            print("Host name is already set to " + oldHostname)
        else:  # if new port differs from old
            print("Updating hostname from " + oldHostname + " with " + hostname)

    try:  # add port number
        oldPort = config.get(ip, "port")  # check if port is present in section
    except:
        config[ip]["port"] = str(port)  # write port to config
    else:
        if oldPort == str(port):
            print("Port is already set to " + oldPort)
        else:  # if new port differs from old
            print("Updating port from " + oldPort + " with " + str(port))

    options = config.options(ip)  # load all options in section

    for option in options:
        if option.startswith(
            "username"
        ):  # if option is username add one to existing users counter
            exUsers += 1

    if verbose:
        print("\n--- Users to add: " + str(len(userList)))
        print("    Existing users: " + str(exUsers))
    else:
        if exUsers >= 1:
            print("\nThere was already " + str(exUsers) + " users for IP '" + ip + "'")

    delUserList = (
        []
    )  # will contain usernames that exist both in section and in the add-list
    if verbose:
        print("\n--- Checking for existing entries ...")
    for i in range(0, len(userList)):  # count up to number if users that is to be added
        for ii in range(
            0, exUsers
        ):  # count up to number of users already in this section
            oldUsername = config.get(
                ip, "username" + str(ii)
            )  # username for 'username#'
            if verbose:
                print(
                    "    Checking new user: "
                    + userList[i]
                    + " with index: "
                    + str(i)
                    + ", against username"
                    + str(ii)
                    + ": "
                    + oldUsername
                )
            if userList[i] == oldUsername:
                print("User " + userList[i] + " already exists")
                if verbose:
                    print("--- Will not add new user with index: " + str(i))
                delUserList.append(userList[i])

    if len(delUserList) >= 1:
        if verbose:
            print(
                "\n--- Not adding "
                + str(len(delUserList))
                + " out of "
                + str(len(userList))
                + " indexes:"
            )
        for delUser in delUserList:
            delUserIndex = userList.index(
                delUser
            )  #  get the index-number for username in add-list
            if verbose:
                print(
                    "    Index: "
                    + str(delUserIndex)
                    + ", Username: "
                    + userList[delUserIndex]
                )
            userList.remove(delUser)  # delete the username from add-list
            cryptPasswdList.pop(
                delUserIndex
            )  # delete the password with that index-number
        if verbose:
            print("    Users left to add: " + str(len(userList)))

    if verbose:
        print("\n--- Adding connection ...")
        print("    IP:            " + ip)
        print("    Host name:     " + hostname)
    config.set(ip, "hostname", hostname)
    if verbose:
        print("    Port:          " + str(port))
    config.set(ip, "port", str(port))

    if len(userList) == 0:
        if verbose:
            print("\n--- No users was left to add")
    else:
        for i in range(
            0 + exUsers, len(userList) + exUsers
        ):  # start counting at number of existing users +1, count up to number of existing users + number of users to be added
            if verbose:
                print("\n    User " + str(i + 1) + ":     " + userList[i - exUsers])
            config[ip]["username" + str(i)] = userList[i - exUsers]

            # passBytes = cryptPasswdList[i - exUsers]
            # passString = passBytes.decode()
            # config[ip]['password' + str(i)] = passString
            if verbose:
                if show:
                    print(
                        "    Password "
                        + str(i + 1)
                        + ": "
                        + decryptPassword(f_key, cryptPasswdList[i - exUsers], verbose)
                    )
                else:
                    print(
                        "    Password "
                        + str(i + 1)
                        + ": "
                        + cryptPasswdList[i - exUsers]
                    )

            config[ip]["password" + str(i)] = cryptPasswdList[i - exUsers]

    with open(connectionFile, "w") as configfile:
        config.write(configfile)
