#-*- coding: UTF-8 -*-
import glob
import logging
import json
from stanfordcorenlp import StanfordCoreNLP
from PetrXmlConverter import *


class FromCorenlpConverter(PetrXmlConverter):
    def __init__(self, input_path, output_path='', corenlp_path='', port=8000, memory='4g', lang='zh', timeout=1500,
                 quiet=True, logging_level=logging.WARNING):
        PetrXmlConverter.__init__(self, input_path, output_path)

        self.corenlp_path = corenlp_path
        if self.corenlp_path == '' and not self.find_corenlp():
            raise IOError('Could not find stanford corenlp.')
        self.nlp = StanfordCoreNLP(self.corenlp_path, port, memory, lang, timeout, quiet, logging_level)

        print('\033[1;32m'+'Starting up StanfordCoreNLP...'+'\033[0m')

    def __del__(self):
        self.nlp.close()
        print('\033[1;32m'+'Corenlp closed!'+'\033[0m')

    def generate_events(self):
        with open(self.input_path, 'r') as source:
            for line in source.readlines():
                # article
                if not len(line) == 0:
                    properties = line.replace('\n', '').split('|')
                    event = {
                        Attr.id: properties[0],
                        Attr.date: properties[4],
                        Attr.source: properties[6],
                        Attr.url: properties[9]
                    }
                    contents = []
                    # #
                    # # split news content which include "title" "reporttime info" and paragraphs by "　　"
                    # #
                    # #
                    # paragraph
                    # change the contents into unicode
                    temp = properties[8].decode("utf-8")
                    paragraphs = temp.split(u"\u3000")
                    # remove the empty str
                    paragraphs = filter(None, paragraphs)
                    for index, p in enumerate(paragraphs):
                        # "\u3000" and "\xa0" means blank character
                        p = p.strip('\r\n').replace(u'\u3000', u'').replace(u'\xa0', u'')
                        if p == "":
                            continue
                        # sentence
                        sentences = self.sep_sentence(event[Attr.id], "e" if index == len(paragraphs) - 1 else index, p)
                        contents.append(sentences)
                    event[Attr.content] = contents
                    self.events.append(event)

    def parse(self, text):
        text = text.encode("utf-8")
        return self.nlp.parse(text)



    def ner(self , text):
        ner_entities = self.nlp.ner(text)
        locations = []
        local_lable = ["STATE_OR_PROVINCE", "COUNTRY", "CITY", "LOCATION", "FACILITY"]
        for entity in ner_entities:
            if entity[1] in local_lable:
                locations.append(entity[0])
        return " ".join(locations)



    def find_corenlp(self):
        corenlp_paths = glob.glob("stanford-corenlp-full-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]")
        if len(corenlp_paths) == 0:
            return False
        else:
            corenlp_paths.sort()
            self.corenlp_path = corenlp_paths[-1]
            return True
