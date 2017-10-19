# -*- coding: utf-8 -*-
from __future__ import division
from elasticSearch.elasticClient import ElasticClient
import os
import codecs
import sys
from pprint import pprint

class RimeFeatures:

	def __init__(self,iC, modelName):	
		self.client = ElasticClient()
		self.iC = iC
		self.type = "RimeFeatures"
		self.iC.initFeatureType(self.type)
		self.modelName = modelName


	def preprocess(self, field, content):
		if field == "ipa":
			content = content.split(",")[0]
			content = content.replace("/","")
			content = content.split(";")[0]
			content = content.replace("stressed ","")
			content = content.replace("noun ","")
			content = content.replace("verb ","")

		elif field == "spell":
			content = content.replace("[","")
			content = content.replace("]","")
			content = content.split(";")[0]
			content = content.split(",")[0]
			content = content.replace("stressed ","")
			content = content.replace("noun ","")
			content = content.replace("verb ","")

		elif field == "syllables":
			content = content.replace("noun ","")
			content = content.replace("verb ","")

		return content.strip()

	def search(self, word):
		
		wObj = self.client.search_word_info(word)
		cleanInfo ={}
		if wObj["hits"]["hits"]:
			wInfo = wObj["hits"]["hits"][0]["_source"]
			cleanInfo["word"] = word
			cleanInfo["ipa"] = self.preprocess("ipa",wInfo["ipa"])
			cleanInfo["spell"] = self.preprocess("spell",wInfo["spell"])
			cleanInfo["syllables"] = self.preprocess("syllables",wInfo["syllables"])

		else:
			cleanInfo = None
			#print word+ " not found"

		return cleanInfo

	def testRime(self, w1, w2):

		if w1[1] == w2[1]:
			return

		w1Info = self.search(w1[0].lower())
		w2Info = self.search(w2[0].lower())

		if not w1Info or not w2Info:
			return

		w1Info["idToken"] = w1[1]
		w2Info["idToken"] = w2[1]
		w1Info["idSentence"] = w1[2]
		w2Info["idSentence"] = w2[2]
		w1Info["idParagraph"] = w1[3]
		w2Info["idParagraph"] = w2[3]
		rimeLength = 0

		for ipa1Elem, ipa2Elem in zip(reversed(w1Info["ipa"]), reversed(w2Info["ipa"])):
			if ipa1Elem == ipa2Elem:
				rimeLength+=1
			else:
				break

		if rimeLength > 1:
			#print w1 + " ----> " + w2 + "\t "+str(rimeLength)
			return w1Info, w2Info, rimeLength
		else:
			return None

	def annotateRimes(self, text):
		paragraphs = text.split("\n\n")
		idToken = 0
		idSentence = 0
		rawWords = []
		totalRimes = 0
		for idParagraph, paragraph in enumerate(paragraphs):
			words=[]
			sents = paragraph.split("\n")
			for sent in sents:
				wordList = sent.split()
				for token in wordList:
					token = token.encode("utf-8").lower().replace(".","").replace(",","").replace("'","").replace("—","").replace("[","").replace("]","").replace("!","").replace('"',"").replace(";","").replace("?","").replace("(","").replace(")","").replace(":","")
					words.append((token, idToken,idSentence,idParagraph))
					rawWords.append(token)
					idToken+=1
				idSentence+=1

			rimes = []
			cache = []
			for wordTupl1 in words:
				for wordTupl2 in words:
					if wordTupl1[0]!=wordTupl2[0] and wordTupl1[1]!=wordTupl2[1] and (wordTupl2[1],wordTupl1[1]) not in cache:
						rimeInfo = self.testRime(wordTupl1,wordTupl2)
						cache.append((wordTupl1[1],wordTupl2[1]))
						if rimeInfo:
							if abs(rimeInfo[0]["idSentence"] - rimeInfo[1]["idSentence"]) < 4:
								rimes.append(rimeInfo)
			pprint(rimes)
			totalRimes+=len(rimes)
		
		print totalRimes
		print rawWords
			




if __name__ == '__main__':
	
	txt = codecs.open("/home/joan/Escritorio/Datasets/poetry/1_theRaven_edgarAllanPoe_male.txt","r",encoding="utf-8").read()
	iRA = RimeAnalyzer()
	iRA.annotateRimes(txt)
