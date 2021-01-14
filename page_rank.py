# coding: utf-8
import os
import json
import time
import math
import networkx as nx
from lxml import etree
import matplotlib.pyplot as plt

start_time = time.time()


count = 0
edgelist = []

parser = etree.XMLParser(recover=True)

# lire le dossier contenant la collection
with os.scandir('XML_Coll_MWI_withSem/') as xml_file:
    for xml in xml_file:
        if count == 0 :
            #count = 2
            doc_id = str(xml.name).split('.')[0]
            tree = etree.parse(xml.path, parser)
            for element in tree.findall('.//link'):
                #print(etree.tostring(element))
                href = element.get("{http://www.w3.org/1999/xlink}href")
                if href is not None :
                    contents = href.split('/')
                    for content in contents :
                        if '.xml' in content :
                            edgelist.append((doc_id, content.split('.')[0]))

D = nx.DiGraph(edgelist)
#nx.draw(D, with_labels=True, font_weight='bold')
#plt.show()
page_rank = nx.pagerank(D, 0.9)


with open('page_rank.json', 'w') as json_file :
    json.dump(page_rank, json_file)

end_time = time.time()

print("took {} min".format((end_time - start_time)/60))
