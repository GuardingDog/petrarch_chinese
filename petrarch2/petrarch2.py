# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import glob
import time
import logging
import argparse
from globalConfigPara import getNullActor as gna
from collections import OrderedDict
import json
import timeRecognition.TimeNormalizer


# petrarch.py
##
# Automated event data coder
##
# SYSTEM REQUIREMENTS
# This program has been successfully run under Mac OS 10.10; it is standard Python 2.7
# so it should also run in Unix or Windows.
#
# INITIAL PROVENANCE:
# Programmers:
#             Philip A. Schrodt
#			  Parus Analytics
#			  Charlottesville, VA, 22901 U.S.A.
#			  http://eventdata.parusanalytics.com
#
#             John Beieler
#			  Caerus Associates/Penn State University
#			  Washington, DC / State College, PA, 16801 U.S.A.
#			  http://caerusassociates.com
#             http://bdss.psu.edu
#
# GitHub repository: https://github.com/openeventdata/petrarch
#
# Copyright (c) 2014	Philip A. Schrodt.	All rights reserved.
#
# This project is part of the Open Event Data Alliance tool set; earlier developments
# were funded in part by National Science Foundation grant SES-1259190
#
# This code is covered under the MIT license
#
# Report bugs to: schrodt735@gmail.com
#
# REVISION HISTORY:
# 22-Nov-13:	Initial version
# Summer-14:	Numerous modifications to handle synonyms in actor and verb dictionaries
# 20-Nov-14:	write_actor_root/text added to parse_Config
# ------------------------------------------------------------------------

import PETRglobals  # global variables
import PETRreader  # input routines
import PETRwriter
import utilities
import PETRtree
from timeRecognition.TimeNormalizer import TimeNormalizer


# ========================== VALIDATION FUNCTIONS ========================== #
from globalConfigPara import getNullActor


def get_version():
    return "1.2.0"


actors=dict()
# ========================== OUTPUT/ANALYSIS FUNCTIONS ========================== #

def open_tex(filename):
    fname = open(filename, 'w')
    '''fname.write('Run time: ',
    print("""
\\documentclass[11pt]{article}
\\usepackage{tikz-qtree}
\\usepackage{ifpdf}
\\usepackage{fullpage}
\\usepackage[landscape]{geometry}
\\ifpdf
    \\pdfcompresslevel=9
    \\usepackage[pdftex,     % sets up hyperref to use pdftex driver
            plainpages=false,   % allows page i and 1 to exist in the same document
            breaklinks=true,    % link texts can be broken at the end of line
            colorlinks=true,
            pdftitle=My Document
            pdfauthor=My Good Self
           ]{hyperref}
    \\usepackage{thumbpdf}
\\else
    \\usepackage{graphicx}       % to include graphics
    \\usepackage{hyperref}       % to simplify the use of \href
\\fi

\\title{Petrarch Output}
\\date{}

\\begin{document}
""", file = fname)'''

    return fname


def close_tex(fname):

    return
    print("\n\\end{document})", file=fname)


# ========================== PRIMARY CODING FUNCTIONS ====================== #


def check_discards(SentenceText):
    """
    Checks whether any of the discard phrases are in SentenceText, giving
    priority to the + matches. Returns [indic, match] where indic
       0 : no matches
       1 : simple match
       2 : story match [+ prefix]
    """
    sent = SentenceText.upper().split()  # case insensitive matching
    #size = len(sent)
    level = PETRglobals.DiscardList
    depart_index = [0]
    discardPhrase = ""

    for i in range(len(sent)):

        if '+' in level:
            return [2, '+ ' + discardPhrase]
        elif '$' in level:
            return [1, ' ' + discardPhrase]
        elif sent[i] in level:
            # print(sent[i],SentenceText.upper(),level[sent[i]])
            depart_index.append(i)
            level = level[sent[i]]
            discardPhrase += " " + sent[i]
        else:
            if len(depart_index) == 0:
                continue
            i = depart_index[0]
            level = PETRglobals.DiscardList
    return [0, '']


def get_issues(SentenceText):
    """
    Finds the issues in SentenceText, returns as a list of [code,count]

    <14.02.28> stops coding and sets the issues to zero if it finds *any*
    ignore phrase

    """
    def recurse(words, path, length):
        if '#' in path:  # <16.06.06 pas> Swapped the ordering if these checks since otherwise it crashes when '#' is a "word" in the text
            return path['#'], length
        elif words and words[0] in path:
            return recurse(words[1:], path[words[0]], length + 1)
        return False

    sent = SentenceText.upper().split()  # case insensitive matching
    issues = []

    index = 0
    while index < len(sent):
        match = recurse(sent[index:], PETRglobals.IssueList, 0)
        if match:
            index += match[1]
            code = PETRglobals.IssueCodes[match[0]]
            if code[0] == '~':  # ignore code, so bail
                return []
            ka = 0
            #gotcode = False
            while ka < len(issues):
                if code == issues[ka][0]:
                    issues[ka][1] += 1
                    break
                ka += 1
            if ka == len(issues):  # didn't find the code, so add it
                issues.append([code, 1])
        else:
            index += 1
    return issues


def get_nullactor(event_dict):
    count=0
    for key, val in sorted(event_dict.items()):
        for sent in val['sents']:
            parsed = event_dict[key]['sents'][sent]['parsed']
            treestr = parsed
            getActor(treestr)
            count+=1
            print(count)
    write_file()
    return event_dict


def getNR(tree):
    while tree.find("NR") != -1:
        startPos = tree.find("NR") + 3
        tree = tree[startPos:]
        endPos = tree.find(" ")
        Name = tree[:endPos]
        if not PETRglobals.ActorDict.has_key(Name):
            add_to_actor(Name)



def add_to_actor(name):
    if name in actors.keys():
        actors[name] +=1
    else:
        actors[name] = 1


def write_file():
    array=sorted(actors.items(), key = lambda kv:(kv[1], kv[0]))
    array.reverse()
    fo = open("nullActor.txt", "w")
    # for name in actors.keys():
    #     fo.write(name + " "+str(actors[name])+"\n")
    for(name,num) in array:
        fo.write(name +" "+str(num)+ "\n")
    fo.close()

def getActor(tree):
    npPos = tree.find("IP") + 2
    tree = tree[npPos:]
    left_br = 0
    first_NP = -1
    i = 0

    def getName(i):
        start = i + 1
        while tree[i] != ' ':
            i += 1
        return tree[start:i]

    while i < len(tree):
        if tree[i] == '(':
            left_br += 1
            if getName(i) == "NP" and left_br == 1:
                first_NP = i
        else:
            if tree[i] == ')':
                left_br -= 1
                if first_NP > 0 and left_br == 0:  ## 找到NP -String
                    break
        i += 1
    getNR(tree[first_NP:i])

def get_releasetime(event_dict):
    releasetimeDic = {}
    for key, val in sorted(event_dict.items()):
        releasetime = event_dict[key]['meta']['date']
        articleId = key.split("-")[0]
        if  articleId not in releasetimeDic :
            releasetimeDic[articleId] = releasetime
        else:
            continue
    return releasetimeDic
def get_reporttime(event_dict , realiseTimeDic):

    pre_tn = TimeNormalizer(isPreferFuture=False)

    reporttimeDic ={}

    for key, val in sorted(event_dict.items()):
        id = key.split("-")
        articleId = id[0]

        reportTimeText = event_dict[key][u"meta"][u"reportTimeText"]
        if not reportTimeText == "":
            reportTime = pre_tn.parse(reportTimeText , realiseTimeDic[articleId])
            if "type" in reportTime.keys() and reportTime["type"] == u"timestamp":
                reporttimeDic[articleId] = reportTime["date"]
            else:
                print( reportTimeText , "reportTimeInfo can not be extract . optimize your logic")
                continue

    return reporttimeDic
# 描述：根据文本内容与报到时间确定句子时间
# 状态：已弃用
# def setSentenceTime(reportTime ,paraghId, paraghSents ):
#
#     tn = TimeNormalizer()
#     for sentenceId in paraghSents :
#         if sentenceId == u"0000" and paraghId == "0001":
#             temp = paraghSents[sentenceId]["content"].strip().split(" ")
#             if len(temp) > 1:
#                 try:
#                     sentenceTime = tn.parse(temp[len(temp)-1] , reportTime)
#                 except:
#                     sentenceTime = {"type": "timestamp", "date": reportTime}
#
#                 if "type" in sentenceTime.keys() and sentenceTime["type"] == u"timestamp":
#                     paraghSents[sentenceId]["sentenceTime"] = sentenceTime["date"]
#                 else:
#                     paraghSents[sentenceId]["sentenceTime"] = reportTime
#             else:
#                 paraghSents[sentenceId]["sentenceTime"] = reportTime
#         elif sentenceId == u"0000":
#             try:
#                 sentenceTime = tn.parse(paraghSents[sentenceId]["content"], reportTime)
#             except:
#                 sentenceTime = {"type" : "timestamp" , "date" : reportTime}
#
#             if "type" in sentenceTime.keys() and sentenceTime["type"] == u"timestamp":
#                 paraghSents[sentenceId]["sentenceTime"] = sentenceTime["date"]
#             else:
#                 paraghSents[sentenceId]["sentenceTime"] = reportTime
#
#         else:
#             lastSentenceId_int = int(sentenceId) - 1
#             lastSentenceId_str = unicode(lastSentenceId_int)
#             lastSentenceId = ""
#             if len(lastSentenceId_str) == 1:
#                 lastSentenceId = u"000" + lastSentenceId_str
#             elif len(lastSentenceId_str) == 2:
#                 lastSentenceId = u"00" + lastSentenceId_str
#             else :
#                 lastSentenceId = u"0" + lastSentenceId_str
#             try:
#                 sentenceTime = tn.parse(paraghSents[sentenceId]["content"], paraghSents[lastSentenceId]["sentenceTime"])
#             except:
#                 sentenceTime = {"type" : "timestamp" , "date" : reportTime}
#
#             if "type" in sentenceTime.keys() and sentenceTime["type"] == u"timestamp":
#                 paraghSents[sentenceId]["sentenceTime"] = sentenceTime["date"]
#             else:
#                 paraghSents[sentenceId]["sentenceTime"] = reportTime
#获得句子级别所有NT节点的父节点
# 目前所观测到的NT节点通常其父节点为NP，并且大部分情况是NT外只有一层NP，此层NP即可包含需要的时间信息
# 例如 几月几日
# 但是也存在需要两层找到的NP节点才能包含所需要的时间信息
# 例如 3月24日至27日
# (NP
#     (NP (NT 3月))
#     (NP (NT 24日)
#         (CC 至)
#         (NT 27日)))
def getNtPar(tree):
    ntParentList = []

    if len(tree.children) > 0 :
        for child in tree.children:
            if child.label == u"NT":

                if child.parent.parent and child.parent.parent.label == u"NP":
                    ntParentList.append(child.parent.parent)
                else:
                    ntParentList.append(child.parent)
            else:
                ntParentList = ntParentList + getNtPar(child)
        return ntParentList
    else:
        return []


def set_nt_textList(sentence):
    # 获取NT节点父节点信息
    parentNode = getNtPar(sentence.tree)
    nodeSet = list(set(parentNode))
    nodeSet.sort(key=parentNode.index)
    ntTextList = []
    if len(nodeSet) > 0:
        for node in list(nodeSet):
            ntTextList.append(utilities.extractText_from_Pharse(node))
    sentence.ntTextList = ntTextList

# 时间识别会返回四种类型
#1、timespan ： 时间段 ， 几号到几号
#       采用
#2、timestamp：时间戳 ， 几号
#       采用
#3、timedelta：时间区间，多少天
#       不采用
#4、error：错误
#       不采用
def set_sentenceTimeByReport(sentence , reportTime ,paragh , sentenceId):
    #判定当前句子时间
    #如果是段落首句则根据报到时间为timebase
    #如果不是首句则根据上一句时间为timebase
    tn_pre = TimeNormalizer(isPreferFuture=False)
    if "0000" == sentenceId :
        timeBase = reportTime
    else:
        lastSentenceId_int = int(sentenceId) - 1
        lastSentenceId_str = unicode(lastSentenceId_int)
        lastSentenceId = ""
        if len(lastSentenceId_str) == 1:
            lastSentenceId = u"000" + lastSentenceId_str
        elif len(lastSentenceId_str) == 2:
            lastSentenceId = u"00" + lastSentenceId_str
        else:
            lastSentenceId = u"0" + lastSentenceId_str
        # TODO：unknown bug need fix
        try:
            timeBase = paragh[lastSentenceId]["sentenceTime"]
        except:
            timeBase = reportTime

    if sentence.ntTextList and len(sentence.ntTextList) > 0:
        timeText = sentence.ntTextList[0]
        try:
            sentenceTime = tn_pre.parse(timeText , timeBase)
            if "error" in sentenceTime.keys():
                sentenceTime =  timeBase
            else :
                if sentenceTime["type"] == "timestamp":
                    sentenceTime = sentenceTime["date"]
                elif sentenceTime["type"] == "timespan" :
                    sentenceTime = sentenceTime["timespan"]
                else:
                    sentenceTime = timeBase

            sentence.sentenceTime =sentenceTime
            paragh[sentenceId]["sentenceTime"] = sentenceTime
        except:
            sentence.sentenceTime =  timeBase
            paragh[sentenceId]["sentenceTime"] = timeBase
    else:
        sentence.sentenceTime = timeBase
        paragh[sentenceId]["sentenceTime"] = timeBase



def do_coding(event_dict):
    """
    Main coding loop Note that entering any character other than 'Enter' at the
    prompt will stop the program: this is deliberate.
    <14.02.28>: Bug: PETRglobals.PauseByStory actually pauses after the first
                sentence of the *next* story
    """

    treestr = ""
    NStory = 0
    NSent = 0
    NEvents = 0
    NEmpty = 0
    NDiscardSent = 0
    NDiscardStory = 0

    logger = logging.getLogger('petr_log')
    times = 0
    sents = 0

    #获得发布时间
    realiseTimeDic = get_releasetime(event_dict)

    if not realiseTimeDic :
        print("realiseTimeDic have no timeinfo ,please check “get_releasetime” method")
    #获得报道时间
    reporttimeDic = get_reporttime(event_dict , realiseTimeDic)


    for key, val in sorted(event_dict.items()):
        NStory += 1
        prev_code = []
        SkipStory = False
        print('\n\nProcessing paragraph {}'.format(key))
        StoryDate = event_dict[key]['meta']['date']
        if  StoryDate  == 'NULL':
            continue

        id = key.split("-")
        articleId = id[0]
        paraghId = id[1]

        #设置发布时间与报道时间，报道时间缺失的按发布时间确定
        val["meta"]["realiseTime"] = realiseTimeDic[articleId]
        if articleId in reporttimeDic.keys():
            val["meta"]["reportTime"] = reporttimeDic[articleId]
        else:
            val["meta"]["reportTime"] = realiseTimeDic[articleId]


        if paraghId == "0000":
            with open("timeinfo.txt", "a") as f:

                f.writelines(("发布时间：" + val["meta"]["realiseTime"]).decode("utf-8").encode("utf-8") + "\n")
                f.writelines(("报道时间：" + val["meta"]["reportTime"]).decode("utf-8").encode("utf-8") + "\n")
        with open("timeinfo.txt", "a") as f:
            f.writelines(("文章段落ID:" + articleId + " " + paraghId + "\n").decode("utf-8").encode("utf-8"))

        for sent in sorted(val['sents']):
            print('\n\nProcessing sentence {}'.format(sent))
            NSent += 1
            if 'parsed' in event_dict[key]['sents'][sent]:
                SentenceID = '{}_{}'.format(key, sent)
                SentenceText = event_dict[key]['sents'][sent]['content']
                SentenceDate = event_dict[key]['sents'][sent][
                    'date'] if 'date' in event_dict[key]['sents'][sent] else StoryDate
                Date = PETRreader.dstr_to_ordate(SentenceDate.split(' ')[0].replace('-', ''))
                parsed = event_dict[key]['sents'][sent]['parsed']
                treestr = parsed
                disc = check_discards(SentenceText)
                if disc[0] > 0:
                    if disc[0] == 1:
                        print("Discard sentence:", disc[1])
                        logger.info('\tSentence discard. {}'.format(disc[1]))
                        NDiscardSent += 1
                        continue
                    else:
                        print("Discard story:", disc[1])
                        logger.info('\tStory discard. {}'.format(disc[1]))
                        SkipStory = False
                        NDiscardStory += 1
                        break

                t1 = time.time()
                try:
                    sentence = PETRtree.Sentence(treestr, SentenceText, Date)
                    '''
                    下面一行是调用句法树分类器
                    '''
                    sentence.classify_tree()

                except Exception as e:

                    message = "ERROR IN PETRARCH2 DO_CODING:" +  SentenceID + "\n" + SentenceText + str(e) + "\n"
                    logging.exception(message)
                    continue
                set_nt_textList(sentence)

                set_sentenceTimeByReport(sentence,val["meta"]["reportTime"],val['sents'] , sent)


                with open("timeinfo.txt", "a") as f:
                    f.writelines(("     句子ID:" + sent + "\n").decode("utf-8").encode("utf-8"))
                    f.write("       "+sentence.txt.decode("utf-8").encode("utf-8")+ "\n")
                    f.write("       时间词列表: ")
                    for text in sentence.ntTextList:
                        f.write(text+",")
                    f.write("\n       句子时间：" +str(sentence.sentenceTime).decode("utf-8").encode("utf-8") + "\n\n")
                timeText = sentence.ntTextList
                sentenceTime = sentence.sentenceTime
                try:
                    coded_events, meta = sentence.get_events()
                except Exception as e:
                    message = "ERROR IN PETRARCH2 DO_CODING:" +  SentenceID + "\n" + SentenceText + str(e) + "\n"
                    logging.exception(message)

                # print("coded_events:",coded_events)
                # print("meta:",meta)

                #print("coded_events:",coded_events)
                #print("meta:",meta)
                # exit()


                # 暂时只走了最后一条分支
                code_time = time.time() - t1
                if PETRglobals.NullVerbs or PETRglobals.NullActors:
                    event_dict[key]['meta'] = meta
                    event_dict[key]['text'] = sentence.txt
                elif PETRglobals.NullActors:
                    event_dict[key]['events'] = coded_events
                    coded_events = None   # skips additional processing
                    event_dict[key]['text'] = sentence.txt
                else:
                    # 16.04.30 pas: we're using the key value 'meta' at two
                    # very different
                    event_dict[key]['meta']['verbs'] = meta
                    # levels of event_dict -- see the code about ten lines below -- and
                    # this is potentially confusing, so it probably would be useful to
                    # change one of those
                del (sentence)

                times += code_time
                sents += 1
                # print('\t\t',code_time)

                if coded_events:
                    event_dict[key]['sents'][sent]['events'] = coded_events
                    event_dict[key]['sents'][sent]['meta'] = meta
                    #print('DC-events:', coded_events) # --
                    #print('DC-meta:', meta) # --
                    #print('+++',event_dict[key]['sents'][sent])  # --
                    if PETRglobals.WriteActorText or PETRglobals.WriteEventText or PETRglobals.WriteActorRoot:
                        text_dict = utilities.extract_phrases(event_dict[key]['sents'][sent], SentenceID)
                        print('DC-td1:',text_dict) # --
                        if text_dict:
                            event_dict[key]['sents'][sent][
                                'meta']['actortext'] = {}
                            event_dict[key]['sents'][sent][
                                'meta']['eventtext'] = {}
                            event_dict[key]['sents'][sent][
                                'meta']['actorroot'] = {}
                            event_dict[key]['sents'][sent][
                                'meta']['eventroot'] = {}
                            event_dict[key]['sents'][sent][
                                'meta']['Source'] = {}
                            event_dict[key]['sents'][sent][
                                'meta']['Target'] = {}
                            event_dict[key]['sents'][sent][
                                'meta']['timeText'] = timeText
                            event_dict[key]['sents'][sent][
                                'meta']['sentenceTime'] = {sentenceTime}
# --                            print('DC1:',text_dict) # --
                            for evt in coded_events:
                                # realLocation = []
                                # location_initial = event_dict[key]['sents'][sent]['ner']
                                #
                                # index1 = SentenceText.find(text_dict[evt][0]) + 1
                                # index2 = SentenceText.find(text_dict[evt][1]) - 1
                                # index3 = SentenceText.find(text_dict[evt][2]) - 1
                                # for loc in location_initial:
                                #     if (SentenceText.find(loc, index1, index2)
                                #             or SentenceText.find(loc, index1, index3)):
                                #         realLocation.append(loc)
                                # event_dict[key]['sents'][sent]['ner'] = realLocation

                                if evt in text_dict:  # 16.04.30 pas bypasses problems with expansion of compounds
                                    event_dict[key]['sents'][sent]['meta'][
                                        'actortext'][evt] = text_dict[evt][:2]
                                    event_dict[key]['sents'][sent]['meta'][
                                        'eventtext'][evt] = text_dict[evt][2]
                                    event_dict[key]['sents'][sent]['meta'][
                                        'actorroot'][evt] = text_dict[evt][3:5]
                                    event_dict[key]['sents'][sent]['meta'][
                                        'eventroot'][evt] = text_dict[evt][5]
                                    event_dict[key]['sents'][sent]['meta'][
                                        'Source'][evt] = text_dict[evt][0]
                                    event_dict[key]['sents'][sent]['meta'][
                                        'Target'][evt] = text_dict[evt][1]

                if coded_events and PETRglobals.IssueFileName != "":
                    event_issues = get_issues(SentenceText)
                    if event_issues:
                        event_dict[key]['sents'][sent]['issues'] = event_issues

                if PETRglobals.PauseBySentence:
                    if len(input("Press Enter to continue...")) > 0:
                        sys.exit()

                prev_code = coded_events
                # NEvents += len(coded_events)
                if coded_events is not None and len(coded_events) == 0:
                    NEmpty += 1
            else:
                logger.info('{} has no parse information. Passing.'.format(SentenceID))
                pass

        if SkipStory:
            event_dict[key]['sents'] = None

    print("\nSummary:")

    """
    print(
        "Stories read:",
        NStory,
        "   Sentences coded:",
        NSent,
        "  Events generated:",
        NEvents)
    print(
        "Discards:  Sentence",
        NDiscardSent,
        "  Story",
        NDiscardStory,
        "  Sentences without events:",
        NEmpty)
    print("Average Coding time = ", times / sents if sents else 0)
    """
# --    print('DC-exit:',event_dict)
    return event_dict


def parse_cli_args():
    """Function to parse the command-line arguments for PETRARCH2."""
    __description__ = """
PETRARCH2
(https://openeventdata.github.io/) (v. 1.0.0)
    """
    aparse = argparse.ArgumentParser(prog='petrarch2',
                                     description=__description__)

    sub_parse = aparse.add_subparsers(dest='command_name')

    parse_command = sub_parse.add_parser('parse', help=""" DEPRECATED Command to run the
                                         PETRARCH parser. Do not use unless you've used it before. If you need to
                                         process unparsed text, see the README""",
                                         description="""DEPRECATED Command to run the
                                         PETRARCH parser. Do not use unless you've used it before.If you need to
                                         process unparsed text, see the README""")
    parse_command.add_argument('-i', '--inputs',
                               help='File, or directory of files, to parse.',
                               required=True)
    parse_command.add_argument('-P', '--parsed', action='store_true',
                               default=False, help="""Whether the input
                               document contains StanfordNLP-parsed text.""")
    parse_command.add_argument('-o', '--output',
                               help='File to write parsed events.',
                               required=True)
    parse_command.add_argument('-c', '--config',
                               help="""Filepath for the PETRARCH configuration
                               file. Defaults to PETR_config.ini""",
                               required=False)

    batch_command = sub_parse.add_parser('batch', help="""Command to run a batch
                                         process from parsed files specified by
                                         an optional config file.""",
                                         description="""Command to run a batch
                                         process from parsed files specified by
                                         an optional config file.""")
    batch_command.add_argument('-c', '--config',
                               help="""Filepath for the PETRARCH configuration
                               file. Defaults to PETR_config.ini""",
                               required=False)

    batch_command.add_argument('-i', '--inputs',
                               help="""Filepath for the input XML file. Defaults to
                               data/text/Gigaword.sample.PETR.xml""",
                               required=False)

    batch_command.add_argument('-o', '--outputs',
                               help="""Filepath for the input XML file. Defaults to
                               data/text/Gigaword.sample.PETR.xml""",
                               required=False)

    nulloptions = aparse.add_mutually_exclusive_group()

    nulloptions.add_argument(
        '-na',
        '--nullactors', action='store_true', default=False,
        help="""Find noun phrases which are associated with a verb generating  an event but are
                                not in the dictionary; an integer giving the maximum number of words follows the command.
                                Does not generate events. """,
        required=False)

    nulloptions.add_argument('-nv', '--nullverbs',
                             help="""Find verb phrases which have source and
                               targets but are not in the dictionary. Does not generate events. """,
                             required=False, action="store_true", default=False)

    args = aparse.parse_args()
    return args


def main(cli_args=None):
    if not cli_args:
        cli_args = parse_cli_args()
    utilities.init_logger('PETRARCH.log')
    logger = logging.getLogger('petr_log')

    PETRglobals.RunTimeString = time.asctime()

    print(cli_args)
    if cli_args.config:
        print('Using user-specified config: {}'.format(cli_args.config))
        logger.info(
            'Using user-specified config: {}'.format(cli_args.config))
        PETRreader.parse_Config(cli_args.config)
    else:
        logger.info('Using default config file.')
        PETRreader.parse_Config(utilities._get_data('data/config/',
                                                    'PETR_config.ini'))

    if cli_args.nullverbs:
        print('Coding in null verbs mode; no events will be generated')
        logger.info(
            'Coding in null verbs mode; no events will be generated')
        # Only get verb phrases that are not in the dictionary but are
        # associated with coded noun phrases
        PETRglobals.NullVerbs = True
    elif cli_args.nullactors:
        print('Coding in null actors mode; no events will be generated')
        logger.info(
            'Coding in null verbs mode; no events will be generated')
        # Only get actor phrases that are not in the dictionary but
        # associated with coded verb phrases
        PETRglobals.NullActors = True
        PETRglobals.NewActorLength = int(cli_args.nullactors)

    read_dictionaries()
    start_time = time.time()
    print('\n\n')

    paths = PETRglobals.TextFileList
    if cli_args.inputs:
        if os.path.isdir(cli_args.inputs):
            if cli_args.inputs[-1] != '/':
                paths = glob.glob(cli_args.inputs + '/*.xml')
            else:
                paths = glob.glob(cli_args.inputs + '*.xml')
        elif os.path.isfile(cli_args.inputs):
            paths = [cli_args.inputs]
        else:
            print(
                '\nFatal runtime error:\n"' +
                cli_args.inputs +
                '" could not be located\nPlease enter a valid directory or file of source texts.')
            sys.exit()

    out = ""  # PETRglobals.EventFileName
    if cli_args.outputs:
        out = cli_args.outputs

    if cli_args.command_name == 'parse':
        run(paths, out, cli_args.parsed)

    else:
        run(paths, out, True)  # <===

    print("Coding time:", time.time() - start_time)

    print("Finished")


def read_dictionaries(validation=False):

    print('Verb dictionary:', PETRglobals.VerbFileName)
    verb_path = utilities._get_data(
        'data/dictionaries',
        PETRglobals.VerbFileName)
    PETRreader.read_verb_dictionary(verb_path)

    print('Actor dictionaries:', PETRglobals.ActorFileList)
    for actdict in PETRglobals.ActorFileList:
        actor_path = utilities._get_data('data/dictionaries', actdict)
        PETRreader.read_actor_dictionary(actor_path)

    print('Agent dictionary:', PETRglobals.AgentFileName)
    agent_path = utilities._get_data('data/dictionaries',
                                     PETRglobals.AgentFileName)
    PETRreader.read_agent_dictionary(agent_path)

    print('Discard dictionary:', PETRglobals.DiscardFileName)
    discard_path = utilities._get_data('data/dictionaries',
                                       PETRglobals.DiscardFileName)
    PETRreader.read_discard_list(discard_path)

    if PETRglobals.IssueFileName != "":
        print('Issues dictionary:', PETRglobals.IssueFileName)
        issue_path = utilities._get_data('data/dictionaries',
                                         PETRglobals.IssueFileName)
        PETRreader.read_issue_list(issue_path)


def run(filepaths, out_file, s_parsed):
    # this is the routine called from main()
    print(filepaths)
    events = PETRreader.read_xml_input(filepaths, s_parsed)
    if not s_parsed:
        events = utilities.stanford_parse(events)

    #print("events_input:",events)
    flag = gna

    if flag:
        get_nullactor(events)

    else:
        updated_events = do_coding(events)
        #print(json.dumps(updated_events, ensure_ascii=False, encoding='utf-8'))
        import globalConfigPara as gcp
        if PETRglobals.NullVerbs:
            PETRwriter.write_nullverbs(updated_events, 'nullverbs.' + out_file)
        elif PETRglobals.NullActors:
            PETRwriter.write_nullactors(updated_events, 'nullactors.txt')
        else:
            PETRwriter.write_events(updated_events, out_file)



def run_pipeline(data, out_file=None, config=None, write_output=True,
                 parsed=False):
    # this is called externally
    utilities.init_logger('PETRARCH.log')
    logger = logging.getLogger('petr_log')
    if config:
        print('Using user-specified config: {}'.format(config))
        logger.info('Using user-specified config: {}'.format(config))
        PETRreader.parse_Config(config)
    else:
        logger.info('Using default config file.')
        logger.info(
            'Config path: {}'.format(
                utilities._get_data(
                    'data/config/',
                    'PETR_config.ini')))
        PETRreader.parse_Config(utilities._get_data('data/config/',
                                                    'PETR_config.ini'))

    read_dictionaries()

    logger.info('Hitting read events...')
    events = PETRreader.read_pipeline_input(data)
    if parsed:
        logger.info('Hitting do_coding')
        updated_events = do_coding(events)
    else:
        events = utilities.stanford_parse(events)
        updated_events = do_coding(events)
    if not write_output:
        output_events = PETRwriter.pipe_output(updated_events)
        return output_events
    elif write_output and not out_file:
        print('Please specify an output file...')
        logger.warning('Need an output file. ¯\_(ツ)_/¯')
        sys.exit()
    elif write_output and out_file:
        PETRwriter.write_events(updated_events, out_file)


if __name__ == '__main__':
    # f_handler = open('out.log', 'w')
    # sys.stdout = f_handler
    main()
