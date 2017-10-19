from __future__ import division
import os
import codecs
from nltk import word_tokenize
from elasticClient import ElasticClient
import requests
from lxml import html
import time

path = "/home/joan/Escritorio/Datasets/LiteraryMerged/chapter_divided/"
e = ElasticClient()
i=0
notFound = set()
for fname in os.listdir(path):

	txt = codecs.open(path+fname,"r",encoding="utf-8").read()
	#tokens = word_tokenize(txt)
	tokens = txt.split()
	nCovered = 0
	
	cache = {}
	start = time.time()

	for token in tokens:
		token = token.lower().replace(".","").replace(",","").replace("'","").replace("—","").replace("[","").replace("]","").replace("!","").replace('"',"").replace(";","").replace("?","").replace("(","").replace(")","").replace(":","")
		if token:
			if token in cache:
				nCovered+=1
			else:
				obj = e.search_word_info(token)
				if obj["hits"]["total"] == 0:
					if "-" in token:
						together = token.replace("-","")
						obj2 = e.search_word_info(token)
						if obj2["hits"]["total"] == 0:
							separated = token.split("-")
							for sep in separated:
								tokens.append(sep)
						else:
							nCovered+=1
					elif token.endswith("s"):
						token = token[:-1]
						tokens.append(token)
					else:
						notFound.add(token)
					
				else:
					cache[token] = obj
					nCovered+=1

		else:
			nCovered+=1
	
	nTokens = len(tokens)
	print "Coverage on file "+fname+" is "+ str(nCovered/nTokens)
	print len(notFound)
	end = time.time()
	print(end - start)
	i+=1
	if i == 10:
		break
	


ahUrlBase = "http://lingorado.com/ipa/"
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
    'Content-Type': 'application/x-www-form-urlencoded'
}
session.headers = headers


for token in notFound:
	print token
	data = {'text_to_transcribe': token, 'submit': 'Show transcription','output_dialect':'br','output_style':'only_tr'}
	page = session.post(ahUrlBase,data=data)
	tree = html.fromstring(page.content)
	ipa = tree.xpath("//div[@id='transcr_output']/span[@class='transcribed_word']//text()")
	if ipa:
		print "found "+token, ipa[0]
		e.insert_word_info(token, "", ipa[0], "")
		print "INSERTED"