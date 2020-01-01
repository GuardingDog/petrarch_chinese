# coding=utf-8
import re
import string
import time
from random import random
from xml.dom.minidom import Document
from enum import Enum
import globalConfigPara as gcp
import logging


class Attr(Enum):
    id = 'id'
    date = 'date'
    source = 'source'
    url = 'url'
    content = 'content'
    text = 'text'
    parse = 'parse'
    ner = 'ner'
    reportTime = "reportTime"
    locationText = "locationText"


class PetrXmlConverter:
    def __init__(self, input_path, output_path=''):
        self.input_path = input_path
        if output_path == '':
            self.output_path = gcp.xml_output_path + gcp.xml_file_name + '.xml'
            # self.output_path = gcp.xml_output_path + input_path.split('/')[-1].split('.')[0] + '.xml'
        else:
            self.output_path = output_path
        self.events = []

    def generate_events(self):
        """
        This method should be overridden depending on the input format of input files.
        """
        with open(self.input_path, 'r') as source:
            event = {
                Attr.id: ''.join(random.sample(string.ascii_letters + string.digits, 8)),
                Attr.date: ''.join(time.strftime("%Y%m%d", time.localtime())),
                Attr.source: 'NULL'
            }
            content = re.sub(r'\s', '', source.read())
            # parse = self.parse(content)
            # event[Attr.content] = self.sep_sentence(parse)
            event[Attr.content] = self.sep_sentence(content)
            print('parse event {0}'.format(event[Attr.id]))
            self.events.append(event)

    def parse(self, text):
        return ''

    def getparseByprops(self,text):
        return ""

    # paragraph preprocess
    #
    def format_text(self, content):
        rule = u"(新华网|中新网|人民网|中新社|新华社|新华网|本报)[\u4e00-\u9fa50-9]{2,10}电"
        pattern = re.compile(rule)

        match = pattern.search(content)
        reportTime = ""
        if match:
            startPos = int(match.span()[0])
            endPos = int(match.span()[1])
            reportTime = content[startPos : endPos]
            content = content.replace(reportTime , "")


        return reportTime , content.replace('\u3000', '').replace('　', '') \
            .replace('。”', '”\n') \
            .replace('。', '\n') \
            .replace('；', '\n') \
            .replace(';', '\n') \
            .replace('?”', '”\n') \
            .replace('？”', '”\n') \
            .replace('?', '\n') \
            .replace('？', '\n') \
            .replace('。\n”', '”\n') \
            .replace("(","（")\
            .replace(")","）")\
            .replace("●", "") \
            .replace("■","")\
            .strip(' \n')
            # .replace('”', "\"") \
            # .replace('“', "\"") \
            # .replace("，", ",") \



    def sep_sentence(self, article_id, paragraph_id, content):

        def format_id(id):
            if not "e" == str(id):
                lenId = len(str(id))
                if lenId == 1:
                    return "000" + str(id)
                elif lenId == 2:
                    return "00" + str(id)
                elif lenId == 3:
                    return "0" + str(id)
                else:
                    print("paragraph_id or sentence_id bigger than 999 , please check segementation function")
                    raise RuntimeError("idError")
            else:
                return "e"

        sentences = []
        reportTime ,content = self.format_text(content)
        for i, sent in enumerate(content.split('\n')):
            # id = article_id + "-" + paragraph_id + _ + sentence_id  "50252-0001_0001"
            try:
                sent = sent.strip('\r\n').replace(u'\xa0', u'')
                if sent == "":
                    continue
                #parse_text = self.parse(sent)
                dict_test = self.getparseByprops(sent)
                parse_text = dict_test["parse"]
                locationText = dict_test["locationText"]
                if type(locationText) is list:
                    locationText = locationText[0][0]
                sent_id = str(article_id) + "-" + format_id(paragraph_id) + "_" + format_id(i)
                print "正在处理:" + sent_id
                sentences.append({
                    Attr.id: sent_id,
                    Attr.text: sent,
                    Attr.parse: parse_text,
                    Attr.ner: self.ner(sent),
                    Attr.reportTime:reportTime,
                    Attr.locationText:locationText
                })
            except Exception as e:
                message = "Error in PetrXmlConverter parse:" + str(article_id) + "\t" + format_id(paragraph_id) + "\t" + format_id(
                    i)
                logging.exception(message)
                continue

        return sentences

    def generate_xml(self):
        xml_doc = Document()
        # <Sentences> element
        xml_root = xml_doc.createElement('Sentences')

        for event in self.events:
            # check keys
            keys_check = [key in event.keys() for key in [Attr.id, Attr.date, Attr.source, Attr.content]]
            keys_check.sort()
            if not keys_check[0]:
                print('\033[1;31m' + 'Event without proper keys. Please check event format.\n{}'.format(
                    event) + '\033[0m')
                continue

            for paragraph in event[Attr.content]:
                for sent in paragraph:
                    # <Text> element
                    xml_text = xml_doc.createElement('Text')
                    text_text = xml_doc.createTextNode('\n' + sent[Attr.text] + '\n')
                    xml_text.appendChild(text_text)

                    # <Parse> element
                    xml_parse = xml_doc.createElement("Parse")
                    parse_text = xml_doc.createTextNode('\n' + sent[Attr.parse] + '\n')
                    xml_parse.appendChild(parse_text)

                    # <Parse> element
                    xml_reportTime= xml_doc.createElement("reportTime")
                    parse_reportTime = xml_doc.createTextNode('\n' + sent[Attr.reportTime] + '\n')
                    xml_reportTime.appendChild(parse_reportTime)
                    # <Parse> element
                    xml_locationText = xml_doc.createElement("locationText")
                    parse_locationText = xml_doc.createTextNode('\n' + sent[Attr.locationText] + '\n')
                    xml_locationText.appendChild(parse_locationText)

                    # <ner> element
                    xml_ner = xml_doc.createElement("Ner")
                    if sent[Attr.ner]:
                        ner_text = xml_doc.createTextNode('\n' + "".join(sent[Attr.ner]) + '\n')
                    else:
                        ner_text = xml_doc.createTextNode('\nNER未提取出地点\n')
                    xml_ner.appendChild(ner_text)

                    # <Sentence> element
                    xml_sentence = xml_doc.createElement('Sentence')
                    xml_sentence.setAttribute('id', sent[Attr.id])
                    xml_sentence.setAttribute('sentence', 'True')
                    xml_sentence.setAttribute('source', event[Attr.source])
                    xml_sentence.setAttribute('date', event[Attr.date])
                    xml_sentence.appendChild(xml_text)
                    xml_sentence.appendChild(xml_reportTime)

                    xml_sentence.appendChild(xml_locationText)

                    xml_sentence.appendChild(xml_ner)
                    xml_sentence.appendChild(xml_parse)

                    xml_root.appendChild(xml_sentence)

        xml_doc.appendChild(xml_root)

        with open(self.output_path, 'w+') as output_file:
            xml_doc.writexml(output_file, newl='\n', encoding='utf-8')

    def print_events(self):
        for event in self.events:
            print('*********************************************************')
            print('event id:', event[Attr.id])
            print('event date:', event[Attr.date])
            print('event source:', event[Attr.source])
            print('event url:', event[Attr.url])
            print('event sentences:')
            for sentence in event[Attr.content]:
                print(sentence[Attr.text])
                print(sentence[Attr.parse])
    def getparseByprops(self):
        return ""

    def run(self):
        self.generate_events()
        self.generate_xml()
