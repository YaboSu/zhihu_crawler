import math
import datetime
import json
from bs4 import BeautifulSoup
from .common import get, post, parseNum


class Person:

    '''
    成员变量：
        lastModified: 信息获取的时间
        pid: 用户标识符
        followees: 关注的人列表
        topics: 关注的话题列表
        followersCount：被关注的人数
        agreeCount：获得的总赞数
        asksCount: 提问的数量
        answersCount：回答的数量
    '''

    def __init__(self, pid, dictResp=None):
        if dictResp is None:
            self.pid = pid
        else:
            self.lastModified = dictResp['lastModified']
            self.pid = dictResp['pid']
            self.pid = dictResp['followees']
            self.topics = dictResp['topics']
            self.followersCount = dictResp['followersCount']
            self.agreeCount = dictResp['agreeCount']
            self.asksCount = dictResp['asksCount']
            self.answersCount = dictResp['answersCount']

    def update(self):
        self.lastModified = str(datetime.datetime.now())
        r = get('http://www.zhihu.com/people/'+self.pid)
        if r.status_code != 200:
            return False
        self._parsePage(r.text)
        return True

    def _parsePage(self, html):
        soup = BeautifulSoup(html)
        profile = soup.find('div', class_='zm-profile-side-following zg-clear').find_all('a')
        # 关注的人数
        followeesCount = parseNum(profile[0].strong.text)
        self.followees = []
        if followeesCount > 0:
            self._getFollowees(followeesCount)  # 获取关注的人
        # 被关注的人数
        self.followersCount = parseNum(profile[1].strong.text)
        # 总的赞同数目
        self.agreeCount = int(soup.find('span', class_='zm-profile-header-user-agree').strong.text)

        profileBlock = soup.find('div', class_='profile-navbar')
        items = profileBlock.find_all('a', class_='item')
        # 提问的数量
        self.asksCount = int(items[1].span.text)
        # 回答的数量
        self.answersCount = int(items[2].span.text)

        topicsFollowedCount = 0
        for a in soup.find_all('a', class_='zg-link-litblue'):
            text = a.strong.text
            if text.endswith('话题'):
                p = text.find('个')
                topicsFollowedCount = int(text[:p])
                break
        self.topics = []
        if topicsFollowedCount > 0:
            self.getTopics(topicsFollowedCount)  # 获取关注的话题

    def _getFollowees(self, count):
        followeesUrl = 'http://www.zhihu.com/people/%s/followees' % (self.pid)
        otherHeaders = {'Referer': 'http://www.zhihu.com/people/'+self.pid}
        htmlText = get(followeesUrl, otherHeaders).text

        soup = BeautifulSoup(htmlText)

        # 每次20个
        for a in soup.find_all('a', class_='zm-item-link-avatar'):
            self.followees.append(a['href'][8:])
        if count > 20:
            _xsrf = soup.find('input', attrs={'name': '_xsrf'})['value']
            otherHeaders = {'Referer': followeesUrl}

            params = json.loads(soup.find('div', class_='zh-general-list')['data-init'])['params']
            for i in range(1, math.ceil(count/20)):
                params['offset'] = i*20
                data = {"_xsrf": _xsrf, "method": 'next', 'params': json.dumps(params)}
                r = post('http://www.zhihu.com/node/ProfileFolloweesListV2', otherHeaders, data)
                for block in r.json()['msg']:
                    followeePid = BeautifulSoup(block).find('a', class_='zm-item-link-avatar')['href'][8:]
                    self.followees.append(followeePid)

    def getTopics(self, count):
        topicsUrl = 'http://www.zhihu.com/people/%s/topics' % (self.pid)
        otherHeaders = {'Referer': 'http://www.zhihu.com/people/'+self.pid}
        soup = BeautifulSoup(get(topicsUrl, otherHeaders).text)

        # 每次20个
        for div in soup.find_all('div', class_='zm-profile-section-main'):
            topic = div.find('a', attrs={"data-tip": True}).strong.text
            self.topics.append(topic)
        if count > 20:
            _xsrf = soup.find('input', attrs={'name': '_xsrf'})['value']
            otherHeaders = {'Referer': topicsUrl}
            for i in range(1, math.ceil(count/20)):
                data = {"_xsrf": _xsrf, "start": 0, 'offset': i*20}
                r = post(topicsUrl, otherHeaders, data)
                moresoup = BeautifulSoup(r.json()['msg'][1])
                for div in moresoup.find_all('div', class_='zm-profile-section-main'):
                    topic = div.find('a', attrs={"data-tip": True}).strong.text
                    self.topics.append(topic)

    def toDict(self):
        dictResp = dict()
        dictResp['lastModified'] = self.lastModified
        dictResp['pid'] = self.pid
        dictResp['followees'] = self.followees
        dictResp['topics'] = self.topics
        dictResp['followersCount'] = self.followersCount
        dictResp['agreeCount'] = self.agreeCount
        dictResp['asksCount'] = self.asksCount
        dictResp['answersCount'] = self.answersCount
        return dictResp

    def __str__(self):
        return str(self.toDict())

    def persist(self, fp):
        json.dump(self.toDict(), fp, ensure_ascii=False)
