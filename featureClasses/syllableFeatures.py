# -*- coding: utf-8 -*-
from __future__ import division
import os
import numpy as np
import utils

class SyllableFeatures:

	def __init__(self,iC, modelName):	
		
		self.iC = iC
		self.type = "SyllableFeatures"
		self.iC.initFeatureType(self.type)
		self.modelName = modelName
	
	def get_stress_stats(self):
		featureNames = [self.type+"_generalStress", self.type+"_generalNoStress", self.type+"_wordStress"]
		functionName = "get_stress_stats"

		#if os.path.isfile(self.iC.featurePath+self.modelName+"_"+functionName):
		#	utils.load_features_from_file(self.iC.featurePath+self.modelName+"_"+functionName, self.iC, self.type)
		#	print "loaded "+functionName
		#	return

		for instance in self.iC.instances:
			totalVerses = 0
			error = 0
			totalCoveredVerses=0
			numGeneralStresses = 0
			numGeneralNoStresses = 0
			numWordStresses = 0

			for stanza in instance.stanzas:
				for verse in stanza["verses"]:
					if len(verse["stress"]) == len(verse["syllableList"]):
						totalCoveredVerses += 1
						for idx, sylls in enumerate(verse["syllableList"]):
							stress = verse["stress"][idx]
							if stress == "/":
								numGeneralStresses+=1
							elif stress == "x":
								numGeneralNoStresses+=1
					else:
						pass
						#print verse["stress"]
						#print verse["syllableList"]

				
				for verse in stanza["verses"]:
					totalVerses+=1
					for sylls in verse["syllableList"]:
						if sylls.isupper():
							numWordStresses+=1
						
			meanWordStress = numWordStresses / totalVerses
			meanGeneralStresses = numGeneralStresses / totalCoveredVerses
			meanGeneralNoStresses = numGeneralNoStresses / totalCoveredVerses

			instance.addFeature(self.type, self.type+"_wordStress", meanWordStress)
			instance.addFeature(self.type, self.type+"_generalNoStress", meanGeneralNoStresses)
			instance.addFeature(self.type, self.type+"_generalStress", meanGeneralStresses)
	
		#utils.save_features_to_file(self.iC.featurePath+self.modelName+"_"+functionName,featureNames,self.iC, self.type)
 	




	
	def get_syllable_stats(self):
		featureNames = [self.type+"_meanNumSyllables", self.type+"_meanSylLength", self.type+"_meanSyllsPerVerse", self.type+"_meanVersesPerStanza"]
		functionName = "get_syllable_stats"

		#if os.path.isfile(self.iC.featurePath+self.modelName+"_"+functionName):
		#	utils.load_features_from_file(self.iC.featurePath+self.modelName+"_"+functionName, self.iC, self.type)
		#	print "loaded "+functionName
		#	return

		for instance in self.iC.instances:
			totalStanzas = len(instance.stanzas)
			totalVerses = 0
			totalWords = len(instance.tokens)
			totalSyllables = 0
			totalSyllLength = 0
			meanNumSyllables = 0
			meanSylLength = 0

			for stanza in instance.stanzas:
				totalVerses += len(stanza["verses"])
				for verse in stanza["verses"]:
					for sylls in verse["syllablesPerWord"]:
						totalSyllables+=len(sylls)
						for syl in sylls:
							totalSyllLength+=len(syl)

			meanSyllsPerVerse = totalSyllables / totalVerses
			meanNumSyllables= totalSyllables / totalWords
			meanSylLength = totalSyllLength / totalSyllables
			versesPerStanza = totalVerses / totalStanzas

			instance.addFeature(self.type, self.type+"_meanNumSyllables", meanNumSyllables)
			instance.addFeature(self.type, self.type+"_meanSyllsPerVerse", meanSyllsPerVerse)
			instance.addFeature(self.type, self.type+"_meanSylLength", meanSylLength)
			instance.addFeature(self.type, self.type+"_meanVersesPerStanza", versesPerStanza)

		#utils.save_features_to_file(self.iC.featurePath+self.modelName+"_"+functionName,featureNames,self.iC, self.type)
 	


	