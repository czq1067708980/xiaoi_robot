#coding:utf-8
"""
requests PyV8
"""
import re
import time
import json
import urllib
import urllib2
from cookielib import CookieJar

import PyV8

myheader={
    "Host": "nlp.xiaoi.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "http://nlp.xiaoi.com/robot/demo/wap/wap-demo.action",
    "Connection": "keep-alive"
        }
base_url = 'http://nlp.xiaoi.com'
ver_path = 'verify.jpg'

class XiaoI:
    def __init__(self):
        self.opener = None
        self.openurl = 'http://i.xiaoi.com/robot/webrobot?&callback=__webrobot__processOpenResponse&data={"type":"open"}&ts=%s'
        self.answer = 'http://i.xiaoi.com/robot/webrobot?&callback=__webrobot_processMsg&data={"sessionId":"%s","robotId":"webbot","userId":"%s","body":{"content":"%s"},"type":"txt"}&ts=%s'
        self.ctxt = PyV8.JSContext()
        self.ctxt.enter()
        jstxt = file('decode.txt').read()
        # 获取JS加密函数
        self.func = self.ctxt.eval(jstxt)
        self.header = myheader
        self.xsession = ''
        self.web_session=''
        self.userid = ''

    def _handleCookie(self, ck):
        return self.func(ck)

    def getTimeStamp(self):
        return time.time()*1000

    def handleCookie(self, respon):
        # 取set-cookie的值
        sc = respon.headers['set-cookie']
        ck = [i.split(';')[0].strip() for i in sc.split(',')]

        # 第一次打开创建session
        if not self.xsession:
            self.xsession = ck[0]

        # 这里会出现3种情况，1第一次打开要求set session 返回3个值，第二次登陆成功只返回
        # nonce 第三次开始则一直返回2个nonce
        if len(ck) == 3:
            cookie = self.xsession + '; ' + ck[2]
        elif len(ck) == 2:
            cookie = self.xsession + '; ' + ck[1]
        else:
            cookie = self.xsession + '; ' + ck[0]
        self.header['Cookie'] = self._handleCookie(cookie)

    def login(self):

        # 第一次打开
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
        req = urllib2.Request(self.openurl%self.getTimeStamp(), headers=self.header)
        respon = self.opener.open(req)
        self.handleCookie(respon)
        html = respon.read()
        infos = eval(re.search(r'{.*}', html).group())
        self.userid = infos['userId']
        self.web_session = infos['sessionId']

    def talk(self, gossip=u'你好'):
        """
        gossip 必须是unicode
        """
        req = urllib2.Request(self.answer%(self.web_session, self.userid, gossip.encode('utf8'), self.getTimeStamp()), headers=self.header)
        respon = self.opener.open(req)
        # 每次打开的时候要处理cookie
        self.handleCookie(respon)

        # 检索文本
        html = respon.read()
        ret = re.findall('"content":"(.*?)"', html)[-1].decode('utf8')
        if ret.endswith('\\r\\n'):
            ret = ret[:ret.rfind('\\r\\n', 1)]
        print ret
        return ret
        
if __name__ == "__main__":
    xiaoi =XiaoI()
    xiaoi.login()
    while True:
        gossip = raw_input(u'请提问:'.encode('gbk')).decode('gbk')
        xiaoi.talk(gossip)
