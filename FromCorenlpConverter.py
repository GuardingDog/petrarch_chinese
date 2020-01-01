#-*- coding: UTF-8 -*-
import glob
import logging
import json
from stanfordcorenlp import StanfordCoreNLP
from PetrXmlConverter import *
import pickle as pk
import numpy as np


class FromCorenlpConverter(PetrXmlConverter):
    def __init__(self, input_path, output_path='', corenlp_path='', port=8000, memory='8g', lang='zh', timeout=1500,
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

    def getparseByprops(self,text):
        props = {"annotators": "ssplit,tokenize,pos,ner,parse,depparse", "pipelineLanguage": "zh",
                 "outputFormat": "json"}
        temp = self.nlp.annotate(text.encode("utf-8"), properties=props)
        dict_json = json.loads(temp, encoding="utf-8")
        dict_sentences = dict_json["sentences"]
        for index, sentence in enumerate(dict_sentences):
            dict_result = {}
            dict_result["index"] = str(index)
            dict_result["parse"] = sentence["parse"]
            dict_result["dependency"] = sentence["enhancedPlusPlusDependencies"]
            dict_result["tokens"] = sentence["tokens"]
            #    dict_result["locationEntity"] = filter(lambda a: a["ner"]  in ["STATE_OR_PROVINCE", "COUNTRY", "CITY", "LOCATION", "FACILITY" ,"GPE"], sentence["entitymentions"])
            ner_entities = sentence["entitymentions"]
            locations = []
            local_lable = ["STATE_OR_PROVINCE", "COUNTRY", "CITY", "LOCATION", "FACILITY", "GPE", "ORGANIZATION"]
            for entity in ner_entities:
                if entity["ner"] in local_lable:
                    locations.append(entity)
            dict_result["locationEntity"] = locations
        locationSet = self.setLocationFeatures(dict_result)
        dict_result["locationText"] = locationSet
        return dict_result





    def getOriginalText(self , tokens, begin, end):
        originalText = ""
        for index in range(begin - 1, end):
            token = tokens[index]["originalText"]
            originalText = originalText + token
        return originalText

    # 设置介词特征，也是第一个特征
    # input: 1.dependency 句中所有依存句法
    #       2.tokenIndex 地点实体的index
    # output:1.boolean 此地点实体是否被介词所修饰
    #            (忽略介词“对”)
    #        2.str 介词文本内容或者token文本
    #     依存句法特征中经试验发现介词修饰的结构
    #     case("名词-index" , "介词-index")
    # 样例：
    # case(高雄县-9, 在-7)
    # name(高雄县-9, 台湾省-8)
    # nmod:prep(发生-10, 高雄县-9)
    def set_prepFeature(self ,dependency, tokenIndex, tokenText, tokens):
        for dep in dependency:
            if dep["dep"] == "case" and tokenIndex >= dep["dependent"] and tokenIndex <= dep["governor"] and dep[
                "dependentGloss"] is not "对":
                originalText = self.getOriginalText(tokens, dep["dependent"], dep["governor"])
                return True, originalText
        return False, tokenText

    def set_assFeature(self ,dependency, tokenIndex):
        for dep in dependency:
            if dep["dep"] == "nmod:assmod" and tokenIndex in [dep["governor"], dep["dependent"]]:
                return True

        return False

    def set_nmodFeature(self ,dependency, tokenIndex):
        for dep in dependency:
            if dep["dep"] == "nmod" and tokenIndex in [dep["governor"], dep["dependent"]]:
                return True

        return False

    def set_nsubjFeature(self ,dependency, tokenIndex):
        for dep in dependency:
            if dep["dep"] == "nsubj" and tokenIndex in [dep["governor"], dep["dependent"]]:
                return True
        return False

    # 设置是否存在于句子主干中
    def set_mainFeature(self ,dependency, tokenIndex):

        for dep in dependency:
            if dep["dep"] == "ROOT":
                verbIndex = dep["dependent"]
                break
        TrunkList = []
        for dep in dependency:
            if verbIndex == dep["governor"]:
                wordIndex = dep["dependent"]
                TrunkList.append(wordIndex)
            if verbIndex == dep["dependent"]:
                wordIndex = dep["governor"]
                TrunkList.append(wordIndex)
        if tokenIndex in TrunkList:
            return True
        else:
            return False

    # 设置是否是宾语成分
    def set_objFeature(self ,dependency, tokenIndex):

        for dep in dependency:
            if dep["dep"] == "dobj" and tokenIndex in [dep["governor"], dep["dependent"]]:
                return True
        return False
    def classifyNB(self , vec2Classify, p0Vec, p1Vec, pClass1):
        p1 = sum(vec2Classify * p1Vec) + np.log(pClass1)  # ln(a*b) = ln(a) + ln(b)
        p0 = sum(vec2Classify * p0Vec) + np.log(1.0 - pClass1)
        if p1 > p0:
            return 1
        else:
            return 0

    def getLocation(self ,features, textinfo):
        with open("F:\git_local2\petrarch_chinese\petrarch2\parameter_result_2.pickle", "rb") as f:
            dict_para = pk.load(f)

        p0V = dict_para["p0V"]
        p1V = dict_para["p1V"]
        pSpam = dict_para["pSpam"]
        loc_text = []
        for index, feature in enumerate(features):
            if self.classifyNB(feature, p0V, p1V, pSpam):
                loc_text.append(textinfo[index][1])
        return loc_text


    def setLocationFeatures(self,dict_result):



        locationEntity = dict_result["locationEntity"]
        dependency = dict_result["dependency"]
        tokens = dict_result["tokens"]
        if locationEntity and len(locationEntity) > 0:
            numLocation = len(locationEntity)
            locationTextList = []
            for location in locationEntity:
                features = []
                textinfo = []
                token_text = location["text"]
                token_index = location["tokenEnd"]
                feature_1, originalText = self.set_prepFeature(dependency, token_index, token_text, tokens)
                feature_2 = self.set_assFeature(dependency, token_index)
                feature_3 = self.set_nmodFeature(dependency, token_index)
                feature_4 = self.set_nsubjFeature(dependency, token_index)
                feature_5 = self.set_mainFeature(dependency, token_index)
                if numLocation == 1:
                    feature_6 = True
                else:
                    feature_6 = False
                feature_7 = self.set_objFeature(dependency, token_index)
                features.append(
                    [int(feature_1), int(feature_2), int(feature_3), int(feature_4), int(feature_5), int(feature_6),
                     int(feature_7)])
                textinfo.append((token_text, originalText))

                locationText = self.getLocation(features,textinfo)
                location["locationText"] = locationText
                if locationText and locationText not in locationTextList :
                    locationTextList.append(locationText)
            return locationTextList
        else:
            return ""





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
