# coding: utf-8

from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
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
englishStemmer = PorterStemmer() #SnowballStemmer("english", ignore_stopwords=True)
tokenizer = RegexpTokenizer(r'\w+')

start_time = time.time()

N = 0
K = 1500
NUM_RUN = "05"
NUM_FILE = "07"
ADDITIONAL_INFO = "_stemmer_porter"
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

# lire le dossier contenant la collection
with os.scandir('XML_Coll_MWI_withSem/') as xml_file:
    for xml in xml_file:
        if count < 1:
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
                    #section_text += "\n\n\n" + sec_path + " : \n"
                    E += 1
                if element.tag == "p":
                    current_p = element
                    p_path = tree.getpath(current_p)
                    elements[doc_id].append(p_path)
                    elements_length[doc_id, p_path] = 0
                    #paragraph_text += "\n\n\n" + p_path + " : \n"
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
                    tokens = tokenizer.tokenize(sentence)
                    for token in tokens:
                        if token.isascii() and token not in stop_words and not token.isnumeric():
                            documents[doc_id] += 1
                            stem_term = englishStemmer.stem(token)
                            # handle section
                            if is_inside_section:
                                #section_text += stem_term + " "
                                elements_length[doc_id, sec_path] += 1
                                if (doc_id, sec_count, stem_term) in tf_sec.keys():
                                    tf_e[doc_id, sec_path, stem_term] += 1
                                else:
                                    tf_e[doc_id, sec_path, stem_term] = 1
                                    if stem_term in ef.keys():
                                        ef[stem_term] += 1
                                    else:
                                        ef[stem_term] = 1
                            # handle paragraph
                            if is_inside_paragraph:
                                #paragraph_text += stem_term + " "
                                elements_length[doc_id, p_path] += 1
                                if (doc_id, sec_count, p_count, stem_term) in tf_p.keys():
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


ROOT = '/article[1]'

for query_id in querys.keys():
    for query in querys[query_id]:
        term = englishStemmer.stem(query)
        for doc_id in documents.keys():
            scores[doc_id] = {}
            # calculate scores for paragraphs in sections in articles
            if term in ef.keys():
                for el_path in elements[doc_id]:
                    if (doc_id, el_path, term) in tf_e.keys():
                        w = (1 + math.log(tf_e[doc_id, el_path, term])) * math.log(E/ef[term])
                        if (doc_id, el_path) in scores[doc_id].keys():
                            scores[doc_id][el_path] += w
                        else:
                            scores[doc_id][el_path] = w
            if term in df.keys():
                if (doc_id, term) in tf.keys():
                    w = (1 + math.log(tf[doc_id, term])) * math.log(N/df[term])
                    if ROOT in scores[doc_id].keys():
                        scores[doc_id][ROOT] += w
                    else:
                        scores[doc_id][ROOT] = w


    grouped_scores = {}
    for doc_id in scores.keys():
        element_with_max_key = ROOT
        max_score = 0.0
        for element in dict(scores[doc_id]).keys():
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
            query_id, doc_id_element[0], i+1, score, groupe_name, doc_id_element[1])
        grouped_scores[doc_id_element] = -1

    with open('run_xml/FaresIbrahimaSolofo_{}_{}_ltn_elements{}.txt'.format(NUM_RUN, NUM_FILE, ADDITIONAL_INFO), 'a') as run_file:
        run_file.write(run)

end_time = time.time()

print("took {} min".format((end_time - start_time)/60))
