# -*- coding: utf-8 -*-
from lxml import etree
import os
import re
from lxml import html
import codecs
import requests
from string import ascii_lowercase
from elasticClient import ElasticClient

baseUrl = 'http://www.dictionary.com/list/'

session = requests.Session()
session.max_redirects = 10000000000
headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}
session.headers = headers

def crawlWordInfo(wordDefLink):
	print wordDefLink
	page = session.get(wordDefLink)
	tree = html.fromstring(page.content)

	syllables = tree.xpath("(//span[@class='me'])[1]/@data-syllable")
	syllables = "".join(syllables)
	
	originalWord = tree.xpath("(//span[@class='me'])[1]//text()")
	originalWord = "".join(originalWord)
	print originalWord

	e = ElasticClient()
	obj = e.search_word_info(originalWord)
	if obj["hits"]["total"] == 0:
		print "no hits"
	else:
		print "FOUND"
		print obj
		return

	ipaPron = tree.xpath("(//div[@class='header-row header-extras pronounce pronset']/div/span[@class='pron ipapron'])[1]//text()")
	ipaPron = "".join(ipaPron)
	spellPron = tree.xpath("(//div[@class='header-row header-extras pronounce pronset']/div/span[@class='pron spellpron'])[1]//text()")
	spellPron = "".join(spellPron)
	print ipaPron,spellPron

	if not spellPron and not ipaPron:
		ipaPron = tree.xpath("(//span[contains(@class,'oneClick-link')])[1]//text()")
		ipaPron = "".join(ipaPron)
		spellPron = tree.xpath("(//span[contains(@class,'oneClick-link')])[2]//text()")
		spellPron = "".join(spellPron)

	if not spellPron and not ipaPron:
		stuff = tree.xpath("//section[@id='source-ahsmd']/div[contains(@class,'source-box')]/p//text()")
		if stuff:
			stuff = stuff[1]
			pieces = stuff.split("(")
			if len(pieces) == 2:
				syllables = "".join(pieces[0])
				ipaPron = "".join(pieces[1])[:-1]

	if not ipaPron:
		ipaPron = tree.xpath("//span[@class='pronset']/span[@class='pron ipapron']/span[@class='dbox-pron']/text()")
		ipaPron = "".join(ipaPron)

	print ipaPron,spellPron

	if ipaPron and spellPron:
		e.insert_word_info(originalWord, syllables, ipaPron, spellPron)
	else:
		print "dont have pron"

for c in ascii_lowercase:
	if c in ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y"]:
		print "HAVE "+c
		continue

	letterUrl = baseUrl + c
	#page = session.get( letterUrl + "/1")
	#tree = html.fromstring(page.content)
	#lastPage = tree.xpath("//div[@class='pagination']/a[contains(text(),'Last')]/@href")
	#lastPage = lastPage[0].split("/")[-1]
	lastPage =9
	current = 1

	while current <= int(lastPage):
		currentURL = letterUrl + "/"+str(current)
		page = session.get( currentURL)
		tree = html.fromstring(page.content)
		wordDefLinks = tree.xpath("//li/span[@class='self-serp-link']/a/@href")

		for wordDefLink in wordDefLinks:
			if wordDefLink == "http://www.dictionary.com/browse/low-pass-filter":
				print "PASOOO"
			else:
				crawlWordInfo(wordDefLink)

		print "Page "+str(current)+" of "+str(lastPage)
		current+=1

	exit()