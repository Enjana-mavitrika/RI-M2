# coding: utf-8

from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
import re  # use regex
import os
import nltk
import json
import time
import math
from lxml import etree
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
tokenizer = word_tokenize #RegexpTokenizer(r'\w+')
from nltk.stem import WordNetLemmatizer 
  
lemmatizer = WordNetLemmatizer() 

start_time = time.time()

# fonction qui ajoute les numéro d'élement sur les 
# xpath, qui pourrait corriger le pb de xpath non reconnus
def process_xpath(xpath) :
    elements = xpath.split('/')
    elements.pop(0)
    new_elements = ''
    for element in elements :
        if '[' not in element :
            new_elements += '/' + element + '[1]'
        else :
            new_elements += '/' + element
    return new_elements

N = 0
K = 1500
NUM_RUN = "06"
NUM_FILE = "05"
k1 = 1.2
b = 0.4
ALPHA_HEADER = 2
groupe_name = "FaresIbrahimaSolofo"
S = 0
P = 0
w_q = {}
scores = {}
scores_sec = {}
scores_p = {}

querys = {
    2009011: ["olive", "oil", "health", "benefit"],
    2009036: ["notting", "hill", "film", "actors"],
    2009067: ["probabilistic", "models", "in", "information", "retrieval"],
    2009073: ["web", "link", "network", "analysis"],
    2009074: ["web", "ranking", "scoring", "algorithm"],
    2009078: ["supervised", "machine", "learning", "algorithm"],
    2009085: ["operating", "system", "mutual", "exclusion"]
}

count = 0
tf = {}
df = {}
documents = {}
sections_length = {}
paragraphs_length = {}
tf_sec = {}
sections = {}
sf = {}
tf_p = {}
paragraphs = {}
pf = {}
sec_path = ""
p_path = ""
h_path = ""
elements = {}
elements_length = {}
tf_e = {}
ef = {}
E = 0
tf_header = {}
tf_sec = {}
parser = etree.XMLParser(recover=True)

# lire le dossier contenant la collection
with os.scandir('XML_Coll_MWI_withSem/') as xml_file:
    for xml in xml_file:
        doc_id = str(xml.name).split('.')[0]
        documents[doc_id] = 0
        tree = etree.parse(xml.path, parser)
        tag_list = []
        sec_count = -1
        elements[doc_id] = []
        p_count = -1
        current_sec = None
        current_h = None
        N += 1
        section_text = ""
        paragraph_text = ""
        for element in tree.iter():
            text = ""
            tokens = []
            text = element.xpath("text()")
            if element.tag == "header":
                current_h = element
                h_path = tree.getpath(current_h)
                elements[doc_id].append(h_path)
                elements_length[doc_id, h_path] = 0
                E += 1
            if element.tag == "sec":
                current_sec = element
                sec_path = tree.getpath(current_sec)
                elements[doc_id].append(sec_path)
                elements_length[doc_id, sec_path] = 0
                E += 1
            # check if element is inside current section
            is_inside_section = False
            is_inside_header = False
            for ancestor in element.iterancestors():
                if ancestor is current_sec or element is current_sec:
                    is_inside_section = True
                if ancestor is current_h or element is current_h:
                    is_inside_header = True
            for sentence in text:
                tokens = tokenizer(sentence)
                for token in tokens:
                    documents[doc_id] += 1
                    if token.isascii() and token not in stop_words and not token.isnumeric():
                        stem_term = lemmatizer.lemmatize(token)
                        # handle header
                        if is_inside_header:
                            if (doc_id, h_path, stem_term) in tf_e.keys():
                                tf_header[doc_id, stem_term] += 1
                            else :
                                tf_header[doc_id, stem_term] = 1
                                if stem_term in ef.keys():
                                    ef[stem_term] += 1
                                else:
                                    ef[stem_term] = 1
                        # handle section
                        if is_inside_section:
                            elements_length[doc_id, sec_path] += 1
                            if (doc_id, sec_path, stem_term) in tf_e.keys():
                                tf_e[doc_id, sec_path, stem_term] += 1
                            else:
                                tf_e[doc_id, sec_path, stem_term] = 1
                                if stem_term in ef.keys():
                                    ef[stem_term] += 1
                                else:
                                    ef[stem_term] = 1
                         # handle documents
                        if (doc_id, stem_term) in tf.keys():
                            tf[doc_id, stem_term] += 1
                        else:
                            tf[doc_id, stem_term] = 1
                            if stem_term in df.keys():
                                df[stem_term] += 1
                            else:
                                df[stem_term] = 1
                        

sum_size = 0
for id in documents.keys():
    sum_size += documents[id]
avgdl = sum_size/N

sum_size_elements = 0
for element_size in elements_length.values():
    sum_size_elements += element_size
avgel = sum_size_elements / E


ROOT = '/article[1]'


for query_id in querys.keys():
    for query in querys[query_id]:
        term = lemmatizer.lemmatize(query)
        for doc_id in documents.keys():
            tf_sec = 0.0
            tf_prime = 0.0
            # calculate tf for elements
            if term in ef.keys():
                for el_path in elements[doc_id]:
                    if (doc_id, el_path, term) in tf_e.keys():
                        tf_sec += tf_e[doc_id, el_path, term]
            
            tf_prime = tf_sec
            if (doc_id, term) in tf_header.keys() :
                tf_prime += tf_header[doc_id, term] * ALPHA_HEADER

            if term in df.keys():
                if (doc_id, term) in tf.keys():
                    qi = (N - df[term] + 0.5) / (df[term] + 0.5)
                    idf = math.log(qi)
                    w = idf * ((tf_prime * (k1 + 1)) / (tf[doc_id, term] +
                                                                k1 * (1 - b + b * (documents[doc_id]/avgdl))))
                    if (doc_id, ROOT) in scores.keys():
                        scores[doc_id, ROOT] += w
                    else:
                        scores[doc_id, ROOT] = w

    run = ""
    last_not_null_max_score = 0.001500
    for i in range(K):
        doc_id_element = max(scores, key=scores.get)
        score = scores[doc_id_element]
        if score == 0.0:
            score = last_not_null_max_score - 0.00000001
        last_not_null_max_score = score
        run += "{} Q0 {} {} {:.8f} {} {}\n".format(
            query_id, doc_id_element[0], i+1, score, groupe_name, process_xpath(doc_id_element[1]))
        scores[doc_id_element] = -1

    with open('run_xml/FaresIbrahimaSolofo_{}_{}_bm25_articles_lematizer_k{}b{}_robertson04.txt'.format(NUM_RUN, NUM_FILE, k1, b), 'a') as run_file:
        run_file.write(run)

end_time = time.time()

print("took {} min".format((end_time - start_time)/60))
