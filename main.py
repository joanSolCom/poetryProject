# -*- coding: utf-8 -*-
import instanceManager
from instanceManager import InstanceCollection

from featureClasses.characterBasedFeatures import CharacterBasedFeatures
from featureClasses.wordBasedFeatures import WordBasedFeatures
from featureClasses.sentenceBasedFeatures import SentenceBasedFeatures
from featureClasses.dictionaryBasedFeatures import DictionaryBasedFeatures
from featureClasses.syntacticFeatures import SyntacticFeatures
from featureClasses.discourseFeatures import DiscourseFeatures
from featureClasses.lexicalFeatures import LexicalFeatures
from featureClasses.rimeFeatures import RimeFeatures
from featureClasses.syllableFeatures import SyllableFeatures

from pprint import pprint

def compute_features(paths, featureGroups, modelName, labelPosition, selectedLabels = None):
	print "Creating Instance Collection"
	iC = instanceManager.createInstanceCollection(paths, labelPosition, "_" ,selectedLabels)
	
	iSyl = SyllableFeatures(iC, modelName)
	iSyl.get_syllable_stats()
	iSyl.get_stress_stats()


	'''
	if "CharacterBasedFeatures" in featureGroups:	
		print "Character based"
		iChar = CharacterBasedFeatures(iC,modelName)
		iChar.get_uppers()
		iChar.get_numbers()
		iChar.get_symbols([","],"commas")
		iChar.get_symbols(["."],"dots")
		iChar.get_symbols(['?',"¿"],"questions")
		iChar.get_symbols(['!','¡'],"exclamations")
		iChar.get_symbols([":"],"colons")
		iChar.get_symbols([";"],"semicolons")
		iChar.get_symbols(['"',"'","”","“", "’"],"quotations")
		iChar.get_symbols(["—","-","_"],"hyphens")
		iChar.get_symbols(["(",")"],"parenthesis")
		iChar.get_in_parenthesis_stats()

	if "WordBasedFeatures" in featureGroups:
		print "Word based"
		iWord = WordBasedFeatures(iC,modelName)
		iWord.get_twothree_words()
		iWord.get_word_stdandrange()
		iWord.get_chars_per_word()
		iWord.get_vocabulary_richness()
		iWord.get_stopwords()
		iWord.get_acronyms()
		iWord.get_firstperson_pronouns()
		iWord.get_proper_nouns()

	if "SentenceBasedFeatures" in featureGroups:
		print "Sentence based"
		iSent = SentenceBasedFeatures(iC,modelName)
		iSent.get_wordsPerSentence_stdandrange()

	if "DictionaryBasedFeatures" in featureGroups:
		print "Dictionary based -> ojo que tarda un ratete"
		iDict = DictionaryBasedFeatures(iC,modelName)
		iDict.get_discourse_markers()
		iDict.get_dict_count()
		iDict.get_interjections()
		iDict.get_mean_mood()

	if "SyntacticFeatures" in featureGroups:
		print "Syntactic Features"
		iSyntactic = SyntacticFeatures(iC,modelName)
		iSyntactic.compute_syntactic_features()

	if "DiscourseFeatures" in featureGroups:
		print "Discourse Features"
		iDiscourse = DiscourseFeatures(iC,modelName)
		iDiscourse.compute_discourse_features()

	if "LexicalFeatures" in featureGroups:
		print "Lexical Features"
		iLexical = LexicalFeatures(iC, modelName)
		addedWords = []
		#addedWords = ["ham","hambeast","chimpout","niggers","disgusting","gender","woman","chick","bang","sex","nationalism","game","sheboon","jew","race","white","rape","hiv","AIDS","obese","christian","fat","hitler","swastika"]
		iLexical.generate_bow_features(100, addedWords)
		#iLexical.get_bow_tfidf(50)
	'''

	return iC

modelName = "poetry"
paths = {}
paths["clean"] = "/home/joan/Escritorio/Datasets/poetry/"
#paths["discParsed"] = "/home/joan/Escritorio/Datasets/hateSpeech/meuCorpusHate/discParsed/"
#paths["synParsed"] = "/home/joan/Escritorio/TENSOR/extracted_revistas/synParsed/"

featureGroups = ["LexicalFeatures","CharacterBasedFeatures", "WordBasedFeatures", "SentenceBasedFeatures", "SyntacticFeatures","DictionaryBasedFeatures"]
suffix = "_".join(featureGroups)
pathArff = "/home/joan/repository/PhD/BESTVersion/outputs/"

labelPosition = 2
labeling = "poet"
print modelName
print featureGroups
print labeling

iC = compute_features(paths, featureGroups, modelName, labelPosition)
print iC
#print "to Arff"
#iC.toArff(pathArff, modelName+"_"+labeling+suffix+".arff")
