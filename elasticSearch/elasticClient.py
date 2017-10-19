from elasticsearch import Elasticsearch
import json
import requests
import sys

class ElasticClient:

	es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

	def create_index(self, INDEX_NAME):
		# since we are running locally, use one shard and no replicas
		request_body = {
			"settings" : {
			"number_of_shards": 1,
			"number_of_replicas": 0
			},
			"mappings":{
				"words":{
					"properties":{
						"word": {
							"type":"string",
							"index":"not_analyzed",
						},
						"syllables":{
							"type":"string",
							"index":"not_analyzed",
						},
						"ipa":{
							"type":"string",
							"index":"not_analyzed",
						},
						"spell":{
							"type":"string",
							"index":"not_analyzed",
						}
					}
				}

			}
		}
		print "creating '%s' index..." % (INDEX_NAME)
		res = self.es.indices.create(index = INDEX_NAME, body = request_body)

	def create_json_object(self, wordName, syllables, ipaPron, spellPron):
		data = {}
		data['word'] = wordName
		data['syllables'] = syllables
		data['ipa'] = ipaPron
		data['spell'] = spellPron
		json_data = json.dumps(data)
		print json_data
		return json_data

	def search_word_info(self,word):
		obj = self.es.search(index='words', body={"query" : {"term" : { "word" : word } } })
		return obj

	def insert_word_info(self, wordName, syllables, ipaPron, spellPron):
		json_data = self.create_json_object(wordName, syllables, ipaPron, spellPron)
		#print json_data
		ret = self.es.index(index='words', doc_type='wordinfo', body=json_data)
		return ret

	def preprocess(self, field, content):
		if not isinstance(content, basestring):
			content = content[0]
			
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

		return content

	def get_all_complete(self, write=False):

		query = {
			'size' : 10000,
			'query': {
			'match_all' : {}
			}
		}
		
		fd = None
		if write:
			fd = open("elasticDump.tsv","w")

		res = self.es.search(index='words', doc_type='wordinfo', body=query, scroll='1m')
		scrollId = res['_scroll_id']
		complete = 0
		incomplete = 0
		total = 0
		while total != res["hits"]["total"]:
			#print res["hits"]["total"]
			#print total
			total+=1
			for doc in res['hits']['hits']:
				w1info = doc["_source"]
				try:
					w1ipa = self.preprocess("ipa",w1info["ipa"])
					w1syllables = self.preprocess("syllables",w1info["syllables"])
				except:
					print w1info 
				if write:
					fd.write(w1info["word"].encode("utf-8")+"\t"+w1ipa.encode("utf-8")+"\t"+w1syllables.encode("utf-8")+"\t"+w1info["spell"].encode("utf-8")+"\n")
				if w1syllables.startswith("["):
					incomplete+=1
				else:
					complete+=1

			res = self.es.scroll(scroll_id = scrollId, scroll = '1m')
			scrollId = res['_scroll_id']

		if write:
			fd.close()
		print "complete " + str(complete)
		print "incomplete "+ str(incomplete)
		print "total " + str(total)

		return

