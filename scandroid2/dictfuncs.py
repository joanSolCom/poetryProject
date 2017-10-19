# scandictfuncs.py 1.1
#
# the Scandroid
# Copyright (C) 2005 Charles Hartman
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. See the accompanying file, gpl.txt, for full
# details.
# OSI Certified Open Source Software
#
# This module holds the class that, rather loosely, contains methods and
# structures connected with the dictionary of syllable-and-stress exceptrions.

import os

TEXTDICT = "/home/joan/repository/poetryProject/scandroid2/scandictionary.txt"

class ScanDict:

    def __init__(self):
        self.Dict = {}
        self.dictopen = None
        self.LoadDictionary()
        
    def LoadDictionary(self):

        self.dictopen = TEXTDICT
        try:
            f = open(self.dictopen, 'rU')
        except IOError as e:			
            print e
            exit()

        for line in f:
            tokens = line.split()		# apostrophes do NOT divide tokens
            if not tokens: continue
            if tokens[0][0] in '#;>\n' or len(tokens[0]) < 1: continue
            self.Dict[tokens[0]] = []
            for t in tokens[1:]:
                if t[0] in '#;>': break			# comment; skip rest of line
                self.Dict[tokens[0]].append(t)
        
        f.close()
