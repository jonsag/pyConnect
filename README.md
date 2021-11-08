# pyConnect

Python script to store remote computers with username, password and port to connect via ssh.

## Functions

* Add hosts with hostname, port, usernames and passwords to host list
* Easy edit list
* Generate key for decryption and encryption
* Generate ssh-rsa key
* Copy id file to remote host by selecting from list
* Select host and user from host list to connect with
   ssh,
   ssh with X-forwarding (-X, -Y),
   sftp
* Run command on multiple hosts by selecting them from list
* scp (coming)
* Stores key and host file in your home directory/.pyConnect

## Usage

 pyconnect <options\>

Options:  
  -c, --connect  
    Connect to remote host  
  -a, --add  
    Add hosts, port, usernames etc.  
  -e, --edit  
    Edit hosts, port, usernames etc.  
  -p, --print  
    Prints all hosts, port, usernames etc. on screen  
  -s, --show  
    Shows passwords in plain text  
  -v, --verbose  
    Verbose output  
  -h, --help  
    Prints this  

## Installation

Just copy everything to were you want it,  
then create a link from your $PATH to pyConnect.py  
