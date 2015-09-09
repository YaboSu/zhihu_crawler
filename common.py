import json
import requests
import logging


def post(url, headers, data):
    session = _getSession()
    response = session.post(url, headers=headers, data=data)
    checkResponse(response)
    return response


def get(url):
    session = _getSession()
    response = session.get(url)
    checkResponse(response)
    return response


def checkResponse(response):
    if response.status_code != 200:
        logging.warning(response.status_code)


def parseNum(text):
    if text[-1] == 'K':
        return int(float(text[:-1])*1000)
    else:
        return int(text)


_session = None
_config = None


def _getSession():
    global _session
    if _session is None:
        _session = _signin()
    return _session


def _getConfig():
    global _config
    if _config is None:
        _config = json.load(open('config.json'))
    return _config


def _signin():
    config = _getConfig()
    session = requests.session()
    r = session.post('http://www.zhihu.com/login/email', data=config['login'], headers=config['headers'])
    loginResult = r.json()
    if loginResult['r'] == 1:
        print('login failed:', loginResult['msg'])
        if loginResult['errcode'] == 1991829:  # 输入验证码
            r = session.get('http://www.zhihu.com/captcha.gif')
            with open('captcha.gif', 'wb') as f:
                f.write(r.content)
            captcha = input('请输入验证码（当前目录下captcha.gif）：')
            config['login']['captcha'] = captcha
            r = session.post('http://www.zhihu.com/login/email', data=config['login'], headers=config['headers'])
            loginResult = r.json()
            if loginResult['r'] == 1:
                print('login failed:', loginResult['msg'])
                exit(1)
            else:
                print('signin sucessfully!')
    logging.basicConfig(filename='zhihu_crawler.log', level=logging.INFO)
    return session
