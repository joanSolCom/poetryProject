# -*- coding: utf-8 -*-
from lxml import etree
import os
import re
from lxml import html
import codecs
from elasticClient import ElasticClient

fd = open("cmudictIPA.txt","r")

lines = fd.read().split("\n")
e = ElasticClient()

for idx,line in enumerate(lines):
	pieces = line.split("\t")
	token = pieces[0]
	ipa = pieces[1]
	syllables = "["+str(pieces[2])+"]"
	spell = pieces[3]

	obj = e.search_word_info(token)
	if obj["hits"]["total"] == 0:
		print "no hits"
		e.insert_word_info(token, syllables, ipa, spell)
		print "inserted"
	else:
		print "FOUND"
		#print obj

	print str(idx)

