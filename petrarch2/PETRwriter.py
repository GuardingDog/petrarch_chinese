# -*- coding: UTF-8 -*-
# SYSTEM REQUIREMENTS
# This program has been successfully run under Mac OS 10.10; it is standard Python 2.7
# so it should also run in Unix or Windows.
#
# INITIAL PROVENANCE:
# Programmer: Philip A. Schrodt
#			  Parus Analytics
#			  Charlottesville, VA, 22901 U.S.A.
#			  http://eventdata.parusanalytics.com
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
# ------------------------------------------------------------------------

from __future__ import print_function
from __future__ import unicode_literals

import PETRglobals  # global variables
import utilities
import codecs
import json
import globalConfigPara as gcp
import PETRtree


def get_actor_text(meta_strg):
    """ Extracts the source and target strings from the meta string. """
    pass


def get_sub_str(original_str, tag, start_pos):
    count = 0
    if tag.startswith("("):
        beg = original_str.find(tag, start_pos)
    else:
        beg = original_str.find(tag, start_pos) - 1
    end = 0
    for index, char in enumerate(original_str[beg:]):
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
        if count == 0:
            end = beg + index + 1
            break
    return beg, end, original_str[beg:end]


def extract_location(tree_str):
    flag1_beg = 0
    flag1_end = 0
    location_list = []
    while flag1_end < len(tree_str):
        flag1_beg, flag1_end, str1 = get_sub_str(tree_str, '(PP', flag1_beg)

        if flag1_beg == -1:
            break
        flag2_end = 0
#TODO(GuardingDog) : Multilayer preposition labels are not considered ，Need to change to iteration
        if not str1.find("(P",4) == -1:
            _, _, prep = get_sub_str(str1, '(P', 4)
            prep = prep.split(' ')[1]
            if prep in ['在', '于', '至', '到']:
                while flag2_end < len(str1):
                    flag2_beg, flag2_end, str2 = get_sub_str(str1, 'NR', flag2_end)
                    if flag2_beg == -2:
                        break
                    location_list.append(str2.split(' ')[1])

            flag1_beg += 4
        else:
            flag1_beg += 4
    return location_list


def write_events_demo(sent, events, meta, output_file):
    print("the output_path:", output_file)
    if output_file:
        f = codecs.open(output_file, encoding='utf-8', mode='a')
        # f.write('\n\n')
        f.write(sent.txt + '\n')
        f.write(sent.treestr + '\n')
        locations = extract_location(sent.treestr)
        if len(locations) > 0:
            f.write(str(json.dumps(locations, ensure_ascii=False, encoding='utf-8')) + '\n')
        print('events:', events)
        for index, event in enumerate(events[0]):
            if events[0][index][2] == 0 and gcp.output_zero_flag == '0':
                continue
            f.write(str(events[0][index]) + '\n')
        # f.write(str(meta) + '\n\n')

        f.close()


def write_events(event_dict, output_file):
    """
    Formats and writes the coded event data to a file in a standard
    event-data format.

    Parameters
    ----------

    event_dict: Dictionary.
                The main event-holding dictionary within PETRARCH.


    output_file: String.
                    Filepath to which events should be written.
    """
    global StorySource
    global NEvents
    global StoryIssues

    event_output = []
    # 测试用
    flag = False
    import globalConfigPara as gcp
    if not gcp.merge_event == "":
        flag = gcp.merge_event

    for key in sorted(event_dict):
        story_dict = event_dict[key]
        if not story_dict['sents']:
            continue    # skip cases eliminated by story-level discard
#        print('WE1',story_dict)
        story_output = []
        filtered_events = utilities.story_filter(story_dict, key)
#        print('WE2',filtered_events)
        if 'source' in story_dict['meta']:
            StorySource = story_dict['meta']['source']
        else:
            StorySource = 'NULL'
        if 'url' in story_dict['meta']:
            url = story_dict['meta']['url']
        else:
            url = ''

        event_temp = []
        event_str_temp = []
        for event in filtered_events:
            story_date = event[0]
            source = event[1]
            target = event[2]
            code = filter(lambda a: not a == '\n', event[3])
            skip_flag = False

            if flag:
                n_code = int(code)
                for pre_event in event_temp:
                    if story_date == pre_event[0] and source == pre_event[1] and target == pre_event[2]:
                        pre_code = int(filter(lambda a: not a == '\n', pre_event[3]))
                        if n_code/10 == pre_code/10:
                            if n_code % 10 <= pre_code %10:
                                skip_flag = True
                                break
                            else:
                                index = event_temp.index(pre_event)
                                del event_temp[index]
                                del event_str_temp[index]
                                break
            if skip_flag:
                continue

            ids = ';'.join(filtered_events[event]['ids'])
   
            if 'issues' in filtered_events[event]:
                iss = filtered_events[event]['issues']
                issues = ['{},{}'.format(k, v) for k, v in iss.items()]
                joined_issues = ';'.join(issues)
            else:
                joined_issues = []

            print('Event: {}\t{}\t{}\t{}\t{}\t{}'.format(story_date, source,
                                                         target, code, ids,
                                                         StorySource))
#            event_str = '{}\t{}\t{}\t{}'.format(story_date,source,target,code)
            # 15.04.30: a very crude hack around an error involving multi-word
            # verbs
            if not isinstance(event[3], basestring):
                event_str = '\t'.join(
                    event[:3]) + '\t010\t' + '\t'.join(event[4:])
            else:
                event_str = '\t'.join(event)
            # print(event_str)
            if joined_issues:
                event_str += '\n\tjoined_issues\t{}\n'.format(joined_issues)
            else:
                event_str += '\n\tjoined_issues\tnull\n'

            if url:
                event_str += '\tids\t{}\n\turl\t{}\n\tStorySource\t{}\n'.format(ids, url, StorySource)
            else:
                event_str += '\tids\t{}\n\tStorySource\t{}\n'.format(ids, StorySource)
            if PETRglobals.WriteContent:
                if 'content' in filtered_events[event]:
                    event_str += '\tcontent\t{}\n'.format(
                        filtered_events[event]['content'])
                else:
                    event_str += '\tcontent\t---\n'
            if PETRglobals.WriteSource:
                if 'Source' in filtered_events[event]:
                    event_str += '\tSource\t{}\n'.format(
                        filtered_events[event]['Source'])
                else:
                    event_str += '\tSource\t---\n'

            if PETRglobals.WriteTarget:
                if 'Target' in filtered_events[event]:
                    event_str += '\tTarget\t{}\n'.format(
                        filtered_events[event]['Target'])
                else:
                    event_str += '\tTarget\t---\n'

            if PETRglobals.WriteActorText:
                if 'actortext' in filtered_events[event]:
                    event_str += '\tactortext\t{}\t{}\n'.format(
                        filtered_events[event]['actortext'][0],
                        filtered_events[event]['actortext'][1])
                else:
                    event_str += '\tactortext\t---\t---\n'
            if PETRglobals.WriteEventText:
                if 'eventtext' in filtered_events[event]:
                    event_str += '\teventtext\t{}\n'.format(
                        filtered_events[event]['eventtext'])
                else:
                    event_str += '\teventtext\t---\n'
            # if True:
            if PETRglobals.WriteActorRoot:
                if 'actorroot' in filtered_events[event]:
                    event_str += '\tactorroot\t{}\t{}\n'.format(
                        filtered_events[event]['actorroot'][0],
                        filtered_events[event]['actorroot'][1])
                else:
                    event_str += '\tactorroot\t---\t---\n'
            if PETRglobals.WriteEventRoot:
                if 'eventroot' in filtered_events[event]:
                    event_str += '\teventroot\t{}\n'.format(
                        filtered_events[event]['eventroot'])
                else:
                    event_str += '\teventroot\t---\n'

            event_str_temp.append(event_str)
            event_temp.append(event)

        story_output += event_str_temp
        story_events = '\n'.join(story_output)
        event_output.append(story_events)

    # Filter out blank lines
    event_output = [event for event in event_output if event]

    if output_file:
        f = codecs.open(output_file, encoding='utf-8', mode='a')
        for str in event_output:
            #             field = str.split('\t')  # debugging
            #            f.write(field[5] + '\n')
            f.write(str + '\n')
        f.close()


def write_nullverbs(event_dict, output_file):
    """
    Formats and writes the null verb data to a file as a set of lines in a JSON format.

    Parameters
    ----------

    event_dict: Dictionary.
                The main event-holding dictionary within PETRARCH.


    output_file: String.
                    Filepath to which events should be written.
    """

    def get_actor_list(item):
        """ Resolves the various ways an actor could be in here """
        if isinstance(item, list):
            return item
        elif isinstance(item, tuple):
            return item[0]
        else:
            return [item]

    event_output = []
    for key, value in event_dict.iteritems():
        if not 'nulls' in value['meta']:
            # print('Error:',value['meta'])  # log this and figure out where it
            # is coming from <later: it occurs for discard sentences >
            continue
        for tup in value['meta']['nulls']:
            if not isinstance(tup[0], int):
                srclst = get_actor_list(tup[1][0])
                tarlst = get_actor_list(tup[1][1])
                jsonout = {'id': key,
                           # <16.06.28 pas> With a little more work we could get the upper/lower
                           'sentence': value['text'],
                           # case version -- see corresponding code in
                           # write_nullactors() -- but
                           'source': ', '.join(srclst),
                           'target': ', '.join(tarlst)}  # hoping to refactor 'meta' and this will do for now.
                if jsonout['target'] == 'passive':
                    continue
                if '(S' in tup[0]:
                    parstr = tup[0][:tup[0].index('(S')]
                else:
                    parstr = tup[0]
                jsonout['parse'] = parstr
                phrstr = ''
                for ist in parstr.split(' '):
                    if ')' in ist:
                        phrstr += ist[:ist.index(')')] + ' '
                jsonout['phrase'] = phrstr

                event_output.append(jsonout)

    if output_file:
        f = codecs.open(output_file, encoding='utf-8', mode='w')
        for dct in event_output:
            f.write('{\n')
            for key in ['id', 'sentence', 'phrase', 'parse']:
                f.write('"' + key + '": "' + dct[key] + '",\n')
            f.write('"source": "' + dct['source'] +
                    '", "target": "' + dct['target'] + '"\n}\n')


def write_nullactors(event_dict, output_file):
    """
    Formats and writes the null actor data to a file as a set of lines in a JSON format.

    Parameters
    ----------

    event_dict: Dictionary.
                The main event-holding dictionary within PETRARCH.


    output_file: String.
                    Filepath to which events should be written.
    """

    global hasnull

    def get_actor_text(evt, txt, index):
        """ Adds code when actor is in dictionary; also checks for presence of null actor """
        global hasnull
        text = txt[index]
        if evt[index].startswith('*') and evt[index].endswith('*'):
            if txt[
                    index]:  # system occasionally generates null strings -- of course... -- so might as well skip these
                hasnull = True
        else:
            text += ' [' + evt[index] + ']'
        return text

    event_output = []
    for key, value in event_dict.iteritems():
        if not value['sents']:
            continue
        for sent in value['sents']:
            if 'meta' in value['sents'][sent]:
                if 'actortext' not in value['sents'][sent]['meta']:
                    continue
                for evt, txt in value['sents'][sent]['meta']['actortext'].iteritems(
                ):  # <16.06.26 pas > stop the madness!!! -- we're 5 levels deep here, which is as bad as TABARI. This needs refactoring!
                    hasnull = False
                    jsonout = {'id': key,
                               'sentence': value['sents'][sent]['content'],
                               'source': get_actor_text(evt, txt, 0),
                               'target': get_actor_text(evt, txt, 1),
                               'evtcode': evt[2],
                               'evttext': ''
                               }
                    if hasnull:
                        if evt in value['sents'][sent]['meta']['eventtext']:
                            jsonout['evttext'] = value['sents'][
                                sent]['meta']['eventtext'][evt]

                        event_output.append(jsonout)

    if output_file:
        f = codecs.open(output_file, encoding='utf-8', mode='w')
        for dct in event_output:
            f.write('{\n')
            for key in ['id', 'sentence', 'source',
                        'target', 'evtcode', 'evttext']:
                f.write('"' + key + '": "' + dct[key] + '",\n')
            f.write('}\n')


def pipe_output(event_dict):
    """
    Format the coded event data for use in the processing pipeline.

    Parameters
    ----------

    event_dict: Dictionary.
                The main event-holding dictionary within PETRARCH.


    Returns
    -------

    final_out: Dictionary.
                StoryIDs as the keys and a list of coded event tuples as the
                values, i.e., {StoryID: [(full_record), (full_record)]}. The
                ``full_record`` portion is structured as
                (story_date, source, target, code, joined_issues, ids,
                StorySource) with the ``joined_issues`` field being optional.
                The issues are joined in the format of ISSUE,COUNT;ISSUE,COUNT.
                The IDs are joined as ID;ID;ID.

    """
    final_out = {}
    for key in event_dict:
        story_dict = event_dict[key]
        if not story_dict['sents']:
            continue    # skip cases eliminated by story-level discard
        filtered_events = utilities.story_filter(story_dict, key)
        if 'source' in story_dict['meta']:
            StorySource = story_dict['meta']['source']
        else:
            StorySource = 'NULL'
        if 'url' in story_dict['meta']:
            url = story_dict['meta']['url']
        else:
            url = ''

        if filtered_events:
            story_output = []
            for event in filtered_events:
                story_date = event[0]
                source = event[1]
                target = event[2]
                code = event[3]

                ids = ';'.join(filtered_events[event]['ids'])

                if 'issues' in filtered_events[event]:
                    iss = filtered_events[event]['issues']
                    issues = ['{},{}'.format(k, v) for k, v in iss.items()]
                    joined_issues = ';'.join(issues)
                    event_str = (story_date, source, target, code,
                                 joined_issues, ids, url, StorySource)
                else:
                    event_str = (story_date, source, target, code, ids,
                                 url, StorySource)

                story_output.append(event_str)

            final_out[key] = story_output
        else:
            pass

    return final_out
