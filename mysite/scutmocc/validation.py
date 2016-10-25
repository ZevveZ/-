# coding: utf-8
import re
import urllib.parse
from http.client import RemoteDisconnected
from urllib.error import URLError
from urllib.request import Request, urlopen
import base64
from itsdangerous import URLSafeTimedSerializer as usts


# 将学号姓名post给统一认证账号系统
def get_content(zxh, xm):
    url = 'http://portal.scut.edu.cn/cmstar/searchAccount.portal'
    # post 三个数据
    post_data = urllib.parse.urlencode({'zxh': zxh, 'xm': xm, 'query': '提交'}).encode('utf-8')
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept - Encoding': 'gzip, deflate',
        'Accept - Language': 'zh - CN, zh;q = 0.8',
        'Cache - Control': 'max - age = 0',
        'Connection': 'keep - alive',
        'Content - Length': '50',
        'Content - Type': 'application / x - www - form - urlencoded',
        'Host': 'portal.scut.edu.cn',
        'Origin': 'http: // portal.scut.edu.cn',
        'Referer': 'http: // portal.scut.edu.cn / cmstar / searchAccount.portal',
        'Upgrade - Insecure - Requests': '1',
        'User - Agent': 'Mozilla / 5.0(X11;Linuxi686) AppleWebKit / 537.36'
                        '(KHTML, likeGecko) UbuntuChromium / 53.0.2785.143Chrome / 53.0.2785.143Safari / 537.36'
        # no cookie
    }
    req = Request(url, post_data, header)
    try:
        resp = urlopen(req)
    except URLError as e:
        if hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code:', e.code)
        elif hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason:', e.reason)
        # 如果出现异常返回False
        return ''
    except RemoteDisconnected as e:
        # 本地没有网络连接
        print(e)
        return ''
    else:
        return str(resp.read(), encoding='utf-8')


# 对网页文本使用正则表达式获得验证的结果
def get_result(content):
    err_pattern = 'errMsg'
    err_re = re.compile(err_pattern)
    # 如果网页中存在errMsg字符串，则验证失败
    if content == '' or err_re.search(content):
        return False
    else:
        return True


def validate(zxh, xm):
    # print(get_result(get_content(zxh, xm)))
    return get_result(get_content(zxh, xm))


# 用于验证邮箱
class Token:
    def __init__(self, security_key):
        self.security_key = security_key
        self.salt = base64.encodebytes(bytes(security_key, encoding='utf-8'))

    def generate_validation__token(self, username):
        serializer = usts(self.security_key)
        return serializer.dumps(username, self.salt)

    def confirm_validation_token(self, token, expiration=3600):
        serializer = usts(self.security_key)
        return serializer.loads(token, max_age=expiration, salt=self.salt)

