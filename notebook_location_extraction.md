## CoreNLP

#### 命名实体识别（Named Entity Recognition，简称NER）

又称作“专名识别”，是指识别**文本中具有特定意义的实体**，主要包括人名、地名、机构名、专有名词等。通常包括两部分:（1）实体边界识别；（2） 确定实体类别（人名、地名、机构名或其他）

增加xml文件在PetrXmlConverter L122

petrarch2.do_coding() L227 添加地点SentenceLocation  l235

在FromCorenlpConverter.ner（）：

![1570450813824](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\1570450813824.png)

在Petr  L94 调用了ner

STATE_OR_PROVINCE

COUNTRY

CITY

LOCATION

FACILITY

- 用extract_location方法会报错越界，把PETRreader 中的L2182-2183注释掉