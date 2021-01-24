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
#from nltk.stem import WordNetLemmatizer 
#from nltk.stem.snowball import SnowballStemmer
#englishStemmer=SnowballStemmer("english", ignore_stopwords=True)
  
#lemmatizer = WordNetLemmatizer() 

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
NUM_RUN = "09"
<<<<<<< HEAD
NUM_FILE = "83"
k1 = 0.6
b = 0.3
=======
NUM_FILE = "64"
k1 = 0.3
b = 0.2
>>>>>>> e42960309d2525ba58e468cc7a4a1e3c2c69600f
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
p_path= ""
elements = {}
elements_length = {}
tf_e = {}
ef = {}
E = 0
parser = etree.XMLParser(recover=True)

page_rank = {}

with open('page_rank.json') as json_file:
    page_rank = json.load(json_file)

# lire le dossier contenant la collection
with os.scandir('XML_Coll_MWI_withSem/') as xml_file:
    for xml in xml_file:
        doc_id = str(xml.name).split('.')[0]
        scores[doc_id] = {}
        documents[doc_id] = 0
        tree = etree.parse(xml.path, parser)
        tag_list = []
        sec_count = -1
        elements[doc_id] = []
        p_count = -1
        current_sec = None
        current_p = None
        N += 1
        section_text = ""
        paragraph_text = ""
        for element in tree.iter():
            text = ""
            tokens = []
            text = element.xpath("text()")
            if element.tag == "sec":
                current_sec = element
                sec_path = tree.getpath(current_sec)
                elements[doc_id].append(sec_path)
                elements_length[doc_id, sec_path] = 0
                E += 1
            if element.tag == "p":
                current_p = element
                p_path = tree.getpath(current_p)
                elements[doc_id].append(p_path)
                elements_length[doc_id, p_path] = 0
                E += 1
            # check if element is inside current section
            is_inside_paragraph = False
            is_inside_section = False
            for ancestor in element.iterancestors():
                if ancestor is current_sec or element is current_sec:
                    is_inside_section = True
                if ancestor is current_p or element is current_p:
                    is_inside_paragraph = True
            for sentence in text:
                tokens = tokenizer(sentence)
                for token in tokens:
                    documents[doc_id] += 1
                    if token.isascii() and token not in stop_words and not token.isnumeric():
                        stem_term = token #englishStemmer.stem(token) #lemmatizer.lemmatize(token)
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
                        
                        # handle paragraph
                        if is_inside_paragraph:
                            elements_length[doc_id, p_path] += 1
                            if (doc_id, p_path, stem_term) in tf_e.keys():
                                tf_e[doc_id, p_path, stem_term] += 1
                            else:
                                tf_e[doc_id, p_path, stem_term] = 1
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
        term = query #englishStemmer.stem(query) #lemmatizer.lemmatize(query)
        for doc_id in documents.keys():
            # calculate scores for paragraphs in sections in articles
            if term in ef.keys():
                for el_path in elements[doc_id]:
                    if (doc_id, el_path, term) in tf_e.keys():
                        qi = (E - ef[term] + 0.5) / (ef[term] + 0.5)
                        idf = math.log(qi)
                        w = idf * ((tf_e[doc_id, el_path, term] * (k1 + 1)) / (tf_e[doc_id, el_path, term] +
                                                             k1 * (1 - b + b * (elements_length[doc_id, el_path]/avgel))))
                        if (doc_id, el_path) in scores[doc_id].keys():
                            scores[doc_id][el_path] += w
                        else:
                            scores[doc_id][el_path] = w
            if term in df.keys():
                if (doc_id, term) in tf.keys():
                    qi = (N - df[term] + 0.5) / (df[term] + 0.5)
                    idf = math.log(qi)
                    w = idf * ((tf[doc_id, term] * (k1 + 1)) / (tf[doc_id, term] +
                                                             k1 * (1 - b + b * (documents[doc_id]/avgdl))))
                    p_rank = 0.0
                    if doc_id in page_rank.keys() :
                        p_rank = page_rank[doc_id]
                    if ROOT in scores[doc_id].keys():
                        scores[doc_id][ROOT] += w + p_rank
                    else:
                        scores[doc_id][ROOT] = w + p_rank


    grouped_scores = {}
    for doc_id in scores.keys():
        element_with_max_key = ROOT
        max_score = 0.0
        for element in dict(scores[doc_id]).keys():
            # intégrer le fetch and browse via log
            if element != ROOT :
                scores[doc_id][element] = scores[doc_id][ROOT] + math.log(scores[doc_id][element])
            if max_score < float(dict(scores[doc_id])[element]):
                max_score = float(dict(scores[doc_id])[element])
                element_with_max_key = element
        grouped_scores[doc_id, element_with_max_key] = max_score
        scores[doc_id] = {}


    run = ""
    last_not_null_max_score = 0.001500
    for i in range(K):
        doc_id_element = max(grouped_scores, key=grouped_scores.get)
        score = grouped_scores[doc_id_element]
        if score == 0.0:
            score = last_not_null_max_score - 0.00000001
        last_not_null_max_score = score
        run += "{} Q0 {} {} {:.8f} {} {}\n".format(
            query_id, doc_id_element[0], i+1, score, groupe_name, process_xpath(doc_id_element[1]))
        grouped_scores[doc_id_element] = -1

    with open('run_xml/FaresIbrahimaSolofo_{}_{}_bm25_elements_k{}b{}_fetch_browse_log_pagerank.txt'.format(NUM_RUN, NUM_FILE, k1, b), 'a') as run_file:
        run_file.write(run)

end_time = time.time()

print("took {} min".format((end_time - start_time)/60))
