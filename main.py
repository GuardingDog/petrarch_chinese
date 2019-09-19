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

# iface参数指Linux的网卡接口，如(eth0,wlan0)，这个参数只支持Linux并且需要root权限
def get_free_port(iface=None):
    s = socket.socket()

    if iface:
        s.setsockopt(socket.SOL_SOCKET, 25, bytes(iface, 'utf8'))

    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()

    return port

def wait_process(port):
    cmd_check = "lsof -i:" + str(port) if env == 0 else "netstat -nao|findstr " + str(port)
    ret = os.popen(cmd_check)
    try:
        # 注意解码方式和cmd要相同，即为"gbk"，否则输出乱码
        str_list = ret.readlines()[-1].decode('gbk')

        ret_list = re.split('', str_list)
        process_pid = list(ret_list[0].split())[1]
        if process_pid:
            return True
        else:
            print('判定端口占用时,出现未知错误')
            return False

    except:
        print ("端口未被使用")
        return False

def kill_process(port):
    cmd_check = "lsof -i:" + str(port) if env == 0 else "netstat -nao|findstr " + str(port)
    ret = os.popen(cmd_check)
    try:
        # 注意解码方式和cmd要相同，即为"gbk"，否则输出乱码
        str_list = ret.readlines()[-1].decode('gbk')

        ret_list = re.split('', str_list)
        process_pid = list(ret_list[0].split())[1]

        cmd_kill='kill -9 ' + str(process_pid) if env == 0 else 'taskkill /pid ' + str(process_pid) + ' /F'
        os.popen(cmd_kill)
        print ("端口已被释放")
    except:
        print ("端口未被使用")



if __name__ == "__main__":
    # If you are using python2, the first two lines are needed.
    reload(sys)
    sys.setdefaultencoding('utf-8')
    env = 0
    print(os.getcwd())
    reader.parse_Config()
    input_path = input_name = xml_output_path = output_path = output_filename = xml_file_name = format_text = corenlp_path = ""
    port = -1
    if not gcp.input_path == "":
        input_path = gcp.input_path
    if not gcp.input_name == "":
        input_name = gcp.input_name
    if not gcp.xml_output_path == "":
        xml_output_path = gcp.xml_output_path
    if not gcp.output_path == "":
        output_path = gcp.output_path
    if not gcp.output_name == "":
        output_filename = gcp.output_name
    if not gcp.xml_file_name == "":
        xml_file_name = gcp.xml_file_name
    if not gcp.format_text == "":
        format_text = gcp.format_text
    if not gcp.corenlp_parse == "":
        flag = gcp.corenlp_parse
    if not gcp.corenlp_path == "":
        corenlp_path = gcp.corenlp_path
    if not gcp.port == -1:# 自选端口情况
        port = gcp.port
        kill_process(port)
        while (wait_process(port)):
            print('端口一直被占用中,30秒后自动检测')
            time.sleep(30)
    else:
        port = get_free_port()
        print("程序将在"+str(port)+"号端口启动")

    formatted_lines = []
    with open(input_path+input_name , 'r') as fp:
        lines = fp.readlines()
        for index, line in enumerate(lines):
            if line[0] == '#':
                new_line = '{}|NULL|NULL|NULL|2018-09-08 00:00:00|NULL|NULL|NULL|{}|NULL\n'.format(index, line.replace('\n', '').replace('#', ''))
                formatted_lines.append(new_line)
    with open(input_path + format_text + '.txt', 'w') as fw:
        fw.writelines(formatted_lines)

    if os.path.exists(output_filename):
        with open(output_filename, 'w') as fw:
            fw.write('')

    #flag = True
    if flag:
        converter = FromCorenlpConverter(input_path + format_text + '.txt', '', corenlp_path, port)

        converter.run()

        converter.__del__()

    args = Namespace(command_name='batch', config=None, inputs=xml_output_path + xml_file_name + '.xml',
                     nullactors=False, nullverbs=False, outputs=output_path + output_filename )
    # args = Namespace(command_name='batch', config=None, inputs='petrarch2/test-ch2.xml', nullactors=False, nullverbs=False, outputs=xml_output_path + 'test-ch2' + '_result.txt')
    petrarch2_main(args)




