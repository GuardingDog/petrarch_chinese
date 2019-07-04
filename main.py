# coding=utf-8
import sys
import os
import re
from argparse import Namespace

from FromCorenlpConverter import FromCorenlpConverter
from petrarch2.petrarch2 import main as petrarch2_main

if __name__ == "__main__":
    # If you are using python2, the first two lines are needed.
    reload(sys)
    sys.setdefaultencoding('utf-8')
    file_name = 'test'
    input_path = 'input/'
    output_path = 'output/'
    corenlp_path = 'stanford-corenlp-full-2018-10-05'
    port = 330

    formatted_lines = []
    with open(input_path + 'raw' + '.txt', 'r') as fp:
        lines = fp.readlines()

        for index, line in enumerate(lines):
            if line[0] == '#':
                new_line = '{}|NULL|NULL|NULL|2018-09-08 00:00:00|NULL|NULL|NULL|{}|NULL\n'.format(index, line.replace('\n', '').replace('#', ''))
                formatted_lines.append(new_line)
    with open(input_path + file_name + '.txt', 'w') as fw:
        fw.writelines(formatted_lines)

    if os.path.exists('evts.test.txt'):
        with open('evts.test.txt', 'w') as fw:
            fw.write('')

    flag = True
    if flag:
        converter = FromCorenlpConverter(input_path + file_name + '.txt', '', corenlp_path, port)

        converter.run()

        converter.__del__()

    args = Namespace(command_name='batch', config=None, inputs=output_path + file_name + '.xml',
                     nullactors=False, nullverbs=False, outputs=output_path + file_name + '_result.txt')
    # args = Namespace(command_name='batch', config=None, inputs='petrarch2/test-ch2.xml', nullactors=False, nullverbs=False, outputs=output_path + 'test-ch2' + '_result.txt')
    petrarch2_main(args)



