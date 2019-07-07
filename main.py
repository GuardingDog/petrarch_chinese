# coding=utf-8
import sys
import os
import re
import globalConfigPara as gcp
import socket
import reader as reader
from argparse import Namespace
import time

from FromCorenlpConverter import FromCorenlpConverter
from petrarch2.petrarch2 import main as petrarch2_main


def wait_process(port):
    ret = os.popen("netstat -nao|findstr " + str(port))
    str_list = ret.read().decode('gbk')

    ret_list = re.split('', str_list)
    try:
        process_pid = list(ret_list[0].split())[-1]
        if process_pid:
            return True
        else:
            print('判定端口占用时,出现未知错误')
            return False

    except:
        print "端口未被使用"
        return False

def kill_process(port):
    ret = os.popen("netstat -nao|findstr " + str(port))
    # 注意解码方式和cmd要相同，即为"gbk"，否则输出乱码
    str_list = ret.read().decode('gbk')

    ret_list = re.split('', str_list)
    try:
        process_pid = list(ret_list[0].split())[-1]
        os.popen('taskkill /pid ' + str(process_pid) + ' /F')
        print "端口已被释放"
    except:
        print "端口未被使用"



if __name__ == "__main__":
    # If you are using python2, the first two lines are needed.
    reload(sys)
    sys.setdefaultencoding('utf-8')
    xml_file_name = 'format_text'
    input_path = 'input/'
    input_name = 'raw.txt'
    xml_output_path = 'output/'
    corenlp_path = 'stanford-corenlp-full-2018-10-05'
    port = 6330

    kill_process(port)
    while(wait_process(port)):
        print('端口一直被占用中,30秒后自动检测')
        time.sleep(30)


    output_path = './'
    output_filename = 'events.txt'

    format_text = 'format_text'



    # reader.parse_Config()
    # if not gcp.input_path == "":
    #     input_path = gcp.input_path
    # if not gcp.input_name == "":
    #     input_name = gcp.input_name
    # if not gcp.xml_output_path == "":
    #     xml_output_path = gcp.xml_output_path
    # if not gcp.output_path == "":
    #     output_path = gcp.output_path
    # if not gcp.output_name == "":
    #     output_filename = gcp.output_name





    formatted_lines = []
    with open(input_path+input_name , 'r') as fp:
        lines = fp.readlines()
        for index, line in enumerate(lines):
            if line[0] == '#':
                new_line = '{}|NULL|NULL|NULL|2018-09-08 00:00:00|NULL|NULL|NULL|{}|NULL\n'.format(index, line.replace('\n', '').replace('#', ''))
                formatted_lines.append(new_line)
    with open(input_path + format_text + '.txt', 'w') as fw:
        fw.writelines(formatted_lines)

    if os.path.exists('evts.test.txt'):
        with open('evts.test.txt', 'w') as fw:
            fw.write('')

    flag = True
    if flag:
        converter = FromCorenlpConverter(input_path + format_text + '.txt', '', corenlp_path, port)

        converter.run()

        converter.__del__()
    print(111)

    args = Namespace(command_name='batch', config=None, inputs=xml_output_path + xml_file_name + '.xml',
                     nullactors=False, nullverbs=False, outputs=xml_output_path + xml_file_name + '_result.txt')
    # args = Namespace(command_name='batch', config=None, inputs='petrarch2/test-ch2.xml', nullactors=False, nullverbs=False, outputs=xml_output_path + 'test-ch2' + '_result.txt')
    petrarch2_main(args)




