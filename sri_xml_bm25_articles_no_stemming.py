# coding: utf-8

import re # use regex
import os
import nltk
import json
import time
import math
from lxml import etree
nltk.download('punkt')
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
englishStemmer=SnowballStemmer("english", ignore_stopwords=True)
from nltk.corpus import wordnet
tokenizer = RegexpTokenizer(r'\w+')

start_time = time.time()

N = 0
S = 0
P = 0
K = 1500
groupe_name = "FaresIbrahimaSolofo"
w_q = {}
scores = {}
scores_sec = {}
scores_p = {}

querys = {
    2009011 : ["olive", "oil", "health", "benefit"],
    2009036 : ["notting", "hill", "film", "actors"],
    2009067 : ["probabilistic", "models", "in", "information", "retrieval"],
    2009073 : ["web", "link", "network", "analysis"],
    2009074 : ["web", "ranking", "scoring", "algorithm"],
    2009078 : ["supervised", "machine", "learning", "algorithm"],
    2009085 : ["operating", "system", "mutual", "exclusion"] 
}

NUM_RUN = "05"
NUM_FILE = "06"
k1 = 0.5
b = 0.3

count = 0
tf = {}
df = {}
documents = {}
tf_sec = {}
sections = {}
sf = {}
tf_p = {}
paragraphs = {}
pf = {}

parser = etree.XMLParser(recover=True)

# lire le dossier contenant la collection 
with os.scandir('XML_Coll_MWI_withSem/') as xml_file :
    for xml in xml_file :
        N += 1
        if count < 1 :
            #count += 1
            doc_id = str(xml.name).split('.')[0]
            #print(doc_id)
            documents[doc_id] = 0
            tree = etree.parse(xml.path, parser)
            tag_list = []
            sec_count = -1
            p_count = -1
            current_sec = None
            current_p = None
            tokens_inside_section = ""
            tokens_inside_paragraph = ""
            for element in tree.iter() :
                #print(element.tag)
                text = ""
                tokens = []
                text = element.xpath("text()")
                for sentence in text :
                    tokens = tokenizer.tokenize(sentence)
                    for token in tokens :
                        documents[doc_id] += 1
                        if token.isascii() and token not in stop_words and not token.isnumeric() :
                            stem_term = token #englishStemmer.stem(token)
                            if (doc_id, stem_term) in tf.keys() :
                                tf[doc_id, stem_term] += 1
                            else :
                                tf[doc_id, stem_term] = 1
                                if stem_term in df.keys() :
                                    df[stem_term] += 1
                                else :
                                    df[stem_term] = 1
            

sum_size = 0
for id in documents.keys() :
    sum_size += documents[id]

avgdl = sum_size/N
print("avdl = ", avgdl)
k1 = 2.0
b = 0.75
print("N = ", N)

#print(tf)
for query_id in querys.keys() :
    for query in querys[query_id] :
        term = query #englishStemmer.stem(query)
        if term in df.keys() :
           for doc in documents.keys() :
                #print("doc = ", doc)
                if (doc, term) in tf.keys() :
                    qi = (N - df[term] + 0.5) / (df[term] + 0.5)
                    idf = math.log(qi)
                    w = idf * ((tf[doc, term] * (k1 + 1)) / (tf[doc, term] + k1 * (1 - b + b * (documents[doc]/avgdl))))
                    if doc in scores.keys() :
                        scores[doc] += w  
                    else :
                        scores[doc] =  w
    
    run = ""
    last_not_null_max_score = 0.001500
    for i in range(K) :
        max_key = max(scores, key=scores.get)
        score = scores[max_key]
        if score == 0.0 :
            score = last_not_null_max_score - 0.00000001
        last_not_null_max_score = score
        run += "{} Q0 {} {} {:.8f} {} /article[1]\n".format(query_id, max_key, i+1, score, groupe_name)
        scores[max_key] = -1

    with open('run_xml/FaresIbrahimaSolofo_{}_{}_bm25_articles_no_stemmer_k{}b{}{}.txt'.format(NUM_RUN, NUM_FILE, k1, b)) as run_file :
        run_file.write(run)

end_time = time.time()

print("took {} min".format((end_time - start_time)/60))
