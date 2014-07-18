#coding:utf-8
"""
requests PyV8
"""
import re
import time
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
        self.url = 'http://nlp.xiaoi.com/robot/demo/wap/wap-demo.action'
        self.ctxt = PyV8.JSContext()
        self.ctxt.enter()
        jstxt = file('decode.txt').read()
        # 获取JS加密函数
        self.func = self.ctxt.eval(jstxt)
        self.header = myheader
        self.session = ''

    def _handleCookie(self, ck):
        return self.func(ck)

    def getTimeStamp(self):
        return time.time()*1000

    def handleCookie(self, respon):
        # 取set-cookie的值
        sc = respon.headers['set-cookie']
        ck = [i.split(';')[0].strip() for i in sc.split(',')]

        # 第一次打开创建session
        if not self.session:
            self.session = ck[0]

        # 这里会出现3种情况，1第一次打开要求set session 返回3个值，第二次登陆成功只返回
        # nonce 第三次开始则一直返回2个nonce
        if len(ck) == 3:
            cookie = self.session + '; ' + ck[2]
        elif len(ck) == 2:
            cookie = self.session + '; ' + ck[1]
        else:
            cookie = self.session + '; ' + ck[0]
        self.header['Cookie'] = self._handleCookie(cookie)

    def login(self):

        # 第一次打开
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
        req = urllib2.Request(self.url, headers=self.header)
        respon = self.opener.open(req)
        self.handleCookie(respon)

        # 获取验证码
        content = respon.read()
        pic = re.findall(r'this.src=\'(.*?)\'',content)[0]
        pic_url = base_url + pic + str(self.getTimeStamp())
        with file(ver_path, 'wb') as f:
            f.write(urllib2.urlopen(pic_url).read())

        # 登陆
        # captcha需要为utf8编码
        captcha = raw_input('please input the verify code:')
        captcha = urllib.urlencode({'captcha':captcha.decode('gbk').encode('utf8')}) 
        req = urllib2.Request(self.url, data=captcha, headers=myheader)
        respon = self.opener.open(req)
        self.handleCookie(respon)

    def talk(self, gossip=u'你好'):
        """
        gossip 必须是unicode
        """
        requestContent = urllib.urlencode({'requestContent': gossip.encode('utf8')})
        req = urllib2.Request(self.url, data=requestContent, headers=self.header)
        respon = self.opener.open(req)

        # 每次打开的时候要处理cookie
        self.handleCookie(respon)

        # 检索文本
        html = respon.read()
        content = re.findall(r'<p class="wap_cn2">(.*?)</p>', html, re.DOTALL)[0]
        ret = content[content.find('</span>')+7:].decode('utf8').strip()
        print ret
        return ret
        
if __name__ == "__main__":
    xiaoi =XiaoI()
    xiaoi.login()
    while True:
        gossip = raw_input(u'请提问:'.encode('gbk')).decode('gbk')
        xiaoi.talk(gossip)
