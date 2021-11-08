#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import random


def createHashFile(hashFileLocation, verbose):
    print("\nCreating hash file at " + hashFileLocation)

    md5hash = random.getrandbits(128)

    print("\nHash value: %032x" % md5hash)

    f = open(hashFileLocation, "w+")

    f.write(str(md5hash))

    f.close()

    print("\nHash File written")