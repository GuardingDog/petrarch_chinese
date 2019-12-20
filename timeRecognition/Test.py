#-*- coding:utf-8 _*-
"""
@author:QingZhi
@file: Test.py
@desc: 测试
@time: 2019/12/15
"""
import sys


from TimeNormalizer import TimeNormalizer # 引入包
reload(sys)
sys.setdefaultencoding("utf-8")
tn = TimeNormalizer(isPreferFuture=True)
res = tn.parse(target="18天" , timeBase="2018-02-10 00:00:00")
print(res)
print(u"u'\u4ece', u'\u5728', u'\u5230', u'\u81ea\u4ece', u'\u79bb', u'\u7531', u'\u987a', u'\u987a\u7740', u'\u6cbf', u'\u6cbf\u7740'")


# res = tn.parse(target=u'晚上8点到上午10点之间') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target=u'9月7号' , timeBase="2018-08-02 00:00:00") # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target=u'2013年二月二十八日下午四点三十分二十九秒', timeBase='2013-02-28 16:30:29') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target=u'我需要大概33天2分钟四秒', timeBase='2013-02-28 16:30:29') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target=u'今年儿童节晚上九点一刻') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target=u'三日') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target=u'7点4') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
# res = tn.parse(target=u'春节') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
# res = tn.parse(target=u'明年重阳节') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
# txt1 = '过两天，那要不就明天吧'
# txt2 = '我下礼拜去你们加吃饭'
# txt3 = '过两个月再说'
# txt4 = '要不还是过两天吧'
# txt5 = '后天吧'
# txt6 = '明天上午10点'
#
# timeBase= '2019-11-24 16:30:29'
# res = tn.parse("明天上午10点")
# print(res)
