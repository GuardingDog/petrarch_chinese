#-*- coding:utf-8 -*-
import sys
import globalConfigPara as gcp
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

def parse_Config():

    def get_config_boolean(optname):

        if parser.has_option('StanfordNLP', optname):
            try:
                result = parser.getboolean('StanfordNLP', optname)
                print(optname, "=", result)
                return result
            except ValueError:
                print(
                    "Error in configFile.ini: " +
                    optname +
                    " value must be `true' or `false'")
                raise
        else:
            return False

    parser = ConfigParser()
    config_path = "configFile.ini"
    confdat = parser.read(config_path)
    if len(confdat) == 0:
        print(
            "未发现配置文件:"+config_path
            )
        print("Terminating program")
        sys.exit()

    try:

        # [Options]
        # input_path = "input/raw.txt"
        # xml_output_path = "output/"
        # xml_output_name = "test123.xml"
        # xml_output_path = "./"
        # output_name = "evts.txt"
        #
        # [StanfordNLP]
        # stanford_dir = ~ / stanford - corenlp /
        # corenlp_parse = True
        gcp.input_path = parser.get('Options', 'input_path')
        gcp.input_name = parser.get('Options', 'input_name')
        gcp.xml_output_path = parser.get('Options' , 'xml_output_path')
        gcp.xml_output_name = parser.get('Options' , 'xml_output_name')
        gcp.xml_file_name = parser.get('Options' , 'xml_file_name')
        gcp.output_path = parser.get('Options' , 'output_path')
        gcp.output_name = parser.get('Options' , 'output_name')
        gcp.corenlp_path = parser.get('StanfordNLP' , 'stanford_dir')
        gcp.corenlp_parse = get_config_boolean('corenlp_parse')
        gcp.format_text = parser.get('Options' , 'format_text')
        gcp.neg_dic_path = parser.get('Options' , 'neg_dic_path')
        gcp.prep_dic_path = parser.get('Options', 'prep_dic_path')
        gcp.output_zero_flag = parser.get('Options' , 'output_zero_flag')

        gcp.port = int(parser.get('Options', 'port'))



    except Exception as e:
        print(
            '配置文件格式出错，请查看此配置文件：',
            config_path)
        print("Terminating program")
        sys.exit()

if __name__ == "__main__":
    parse_Config()