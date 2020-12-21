# coding: utf-8

from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
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
englishStemmer = SnowballStemmer("english", ignore_stopwords=True)
tokenizer = RegexpTokenizer(r'\w+')

start_time = time.time()

N = 0
K = 1500
NUM_RUN = "04"
NUM_FILE = "09"
ADDITION_INFO = ""
k1 = 2.0
b = 0.5
groupe_name = "FaresIbrahimaSolofo"
S = 0
P = 0
groupe_name = "FaresIbrahimaSolofo"
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

querys_2 = dict(querys)


# print(querys)

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

parser = etree.XMLParser(recover=True)

# lire le dossier contenant la collection
with os.scandir('XML_Coll_MWI_withSem/') as xml_file:
    for xml in xml_file:
        if count < 500:
            #count += 1
            doc_id = str(xml.name).split('.')[0]
            scores[doc_id] = {}
            documents[doc_id] = 0
            tree = etree.parse(xml.path, parser)
            tag_list = []
            sec_count = -1
            sections[doc_id] = []
            paragraphs[doc_id] = []
            p_count = -1
            current_sec = None
            current_p = None
            N += 1
            #tokens_inside_section = ""
            #tokens_inside_paragraph = ""
            for element in tree.iter():
                text = ""
                tokens = []
                text = element.xpath("text()")
                if element.tag == "sec" and element.getparent().tag == "bdy":
                    current_sec = element
                    sec_count += 1  # section suivante
                    p_count = -1  # redemarrer paragraphe
                    #tokens_inside_section += "\n\n"
                    sections[doc_id].append(sec_count)
                    sections_length[doc_id, sec_count] = 0
                    S += 1
                if element.tag == "p" and element.getparent().tag == "sec":
                    current_p = element
                    p_count += 1  # paragraphe suivante
                    #tokens_inside_paragraph += "\n\n\n\n"
                    paragraphs[doc_id].append((sec_count, p_count))
                    paragraphs_length[doc_id, sec_count, p_count] = 0
                    P += 1
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
                                sections_length[doc_id, sec_count] += 1
                                #tokens_inside_section += " " + stem_term
                                if (doc_id, sec_count, stem_term) in tf_sec.keys():
                                    tf_sec[(doc_id, sec_count, stem_term)] += 1
                                else:
                                    tf_sec[(doc_id, sec_count, stem_term)] = 1
                                    if stem_term in sf.keys():
                                        sf[stem_term] += 1
                                    else:
                                        sf[stem_term] = 1
                            # handle paragraph
                            if is_inside_paragraph:
                                # print(element.tag)
                                #tokens_inside_paragraph += " " + stem_term
                                paragraphs_length[doc_id, sec_count, p_count] += 1
                                if (doc_id, sec_count, p_count, stem_term) in tf_p.keys():
                                    tf_p[(doc_id, sec_count,
                                          p_count, stem_term)] += 1
                                else:
                                    tf_p[(doc_id, sec_count,
                                          p_count, stem_term)] = 1
                                    if stem_term in pf.keys():
                                        pf[stem_term] += 1
                                    else:
                                        pf[stem_term] = 1
                            # handle documents
                            if (doc_id, stem_term) in tf.keys():
                                tf[doc_id, stem_term] += 1
                            else:
                                tf[doc_id, stem_term] = 1
                                if stem_term in df.keys():
                                    df[stem_term] += 1
                                else:
                                    df[stem_term] = 1
            # print(tokens_inside_paragraph)


# # add synset of each term in queries
# # for key in querys.keys() :
# #     for term in querys[key] :
# #         for syns in wordnet.synsets(term)[:6] :
# #             syn = syns.lemmas()[0].name().lower()
# #             stem = englishStemmer.stem(syn)
# #             if syn not in querys[key] and stem in df.keys() :
# #                 querys_2[key].append(syn)
#                 #print("syn of ", term, " = ", syn)

# #print(querys)
# #print(querys_2)

sum_size = 0
for id in documents.keys():
    sum_size += documents[id]
avgdl = sum_size/N

sum_size_section = 0
for section_size in sections_length.values():
    sum_size_section += section_size
avgsl = sum_size_section / S

sum_size_paragraph = 0
for paragraph_size in paragraphs_length.values():
    sum_size_paragraph += paragraph_size
avgpl = sum_size_paragraph / P


ROOT = '/article[1]/bdy[1]'

for query_id in querys.keys():
    for query in querys[query_id]:
        term = englishStemmer.stem(query)
        for doc_id in documents.keys():
            scores[doc_id] = {}
            # calculate scores for paragraphs in sections in articles
            if term in pf.keys():
                for (sec_id, p_id) in paragraphs[doc_id]:
                    if (doc_id, sec_id, p_id, term) in tf_p.keys():
                        qi = (P - pf[term] + 0.5) / (pf[term] + 0.5)
                        idf = math.log(qi)
                        w = idf * ((tf_p[doc_id, sec_id, p_id, term] * (k1 + 1)) / (tf_p[doc_id, sec_id, p_id, term] +
                                                             k1 * (1 - b + b * (paragraphs_length[doc_id, sec_id, p_id]/avgpl))))
                        if (doc_id, sec_id, p_id) in scores[doc_id].keys():
                            scores[doc_id]['{}/sec[{}]/p[{}]'.format(ROOT, sec_id + 1, p_id + 1)] += w
                        else:
                            scores[doc_id]['{}/sec[{}]/p[{}]'.format(ROOT, sec_id + 1, p_id + 1)] = w
            # calculate scores for sections in articles
            if term in sf.keys():
                for sec_id in sections[doc_id]:
                    if (doc_id, sec_id, term) in tf_sec.keys():
                        qi = (S - sf[term] + 0.5) / (sf[term] + 0.5)
                        idf = math.log(qi)
                        w = idf * ((tf_sec[doc_id, sec_id, term] * (k1 + 1)) / (tf_sec[doc_id, sec_id, term] +
                                                             k1 * (1 - b + b * (sections_length[doc_id, sec_id]/avgsl))))
                        if (doc_id, sec_id) in scores[doc_id].keys() :
                            scores[doc_id]['{}/sec[{}]'.format(ROOT, sec_id + 1)] += w
                        else:
                            scores[doc_id]['{}/sec[{}]'.format(ROOT, sec_id + 1)] = w
            # calculate scores for articles
            if term in df.keys():
                if (doc_id, term) in tf.keys():
                    qi = (N - df[term] + 0.5) / (df[term] + 0.5)
                    idf = math.log(qi)
                    w = idf * ((tf[doc_id, term] * (k1 + 1)) / (tf[doc_id, term] +
                                                             k1 * (1 - b + b * (documents[doc_id]/avgdl))))
                    if ROOT in scores[doc_id].keys():
                        scores[doc_id]['/articles[1]'] += w
                    else:
                        scores[doc_id]['/articles[1]'] = w

    grouped_scores = {}
    for doc_id in scores.keys():
        element_with_max_key = "/articles[1]"
        max_score = 0.0
        for element in dict(scores[doc_id]).keys():
            if max_score < float(dict(scores[doc_id])[element]):
                max_score = float(dict(scores[doc_id])[element])
                element_with_max_key = element
        grouped_scores[doc_id, element_with_max_key] = max_score
        scores[doc_id] = {}
    print(grouped_scores)
    #print(scores)
# print(scores)
# with open('run_xml/scores.json', 'w') as outfile:
#     json.dump(scores, outfile)


#     #print(scores)
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

    with open('run_xml/FaresIbrahimaSolofo_{}_{}_bm25_articles_steming_k{}b{}{}.txt'.format(NUM_RUN, NUM_FILE, k1, b, ADDITION_INFO), 'a') as run_file:
        run_file.write(run)

end_time = time.time()

print("took {} min".format((end_time - start_time)/60))
