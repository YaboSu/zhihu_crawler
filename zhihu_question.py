import math
import datetime
import json
from bs4 import BeautifulSoup
from .common import get, post, parseNum


class Question:

    '''
    成员变量：
        lastModified: 信息获取的时间
        qid: 问题标识符
        title: 问题的标题
        detail: 问题内容
        tags: 问题标签
        followersCount: 关注的数量
        answers: 问题的回答
    '''

    def __init__(self, qid, dictResp=None):
        if dictResp is None:
            self.qid = qid
        else:
            self.lastModified = dictResp['lastModified']
            self.qid = dictResp['qid']
            self.title = dictResp['title']
            self.detail = dictResp['detail']
            self.tags = dictResp['tags']
            self.followersCount = dictResp['followersCount']
            self.answers = dictResp['answers']

    def update(self):
        '''
        更新Question，并获取Answers
        '''
        self.lastModified = str(datetime.datetime.now())

        qurl = 'http://www.zhihu.com/question/%d' % (self.qid)
        r = get(qurl)
        if r.status_code != 200:
            return False

        soup = BeautifulSoup(r.text)
        # 标题
        self.title = soup.find('h2', class_='zm-item-title').text.strip()
        # 内容
        self.detail = soup.find('div', id='zh-question-detail').div.text.strip()
        # 所属的话题标签
        self.tags = [a.string.strip() for a in soup.find_all("a", class_='zm-item-tag')]
        # 关注人数
        followersCountBlock = soup.find('div', class_='zg-gray-normal')
        if followersCountBlock is None or followersCountBlock.strong is None:
            # 当”还没有人关注该问题” followersCountBlock.strong is None
            self.followersCount = 0
        else:
            self.followersCount = parseNum(followersCountBlock.strong.text)

        self.answers = []
        # 回答数目
        answersCountBlock = soup.find('h3', id='zh-question-answer-num')
        if answersCountBlock is None:
            if soup.find('span', class_='count') is not None:
                answersCount = 1
            else:
                answersCount = 0
        else:
            answersCount = int(answersCountBlock['data-num'])

        # 答案部分 每次50个
        for block in soup.find_all('div', class_='zm-item-answer'):
            if block.find('div', class_='answer-status') is not None:
                continue  # 忽略建议修改的答案
            self.answers.append(self._extractAnswer(block))
        if answersCount > 50:
            _xsrf = soup.find('input', attrs={'name': '_xsrf'})['value']
            otherHeaders = {'Referer': qurl}
            for i in range(1, math.ceil(answersCount/50)):  # more answers
                data = {"_xsrf": _xsrf, "method": 'next', 'params': '{"url_token": %d, "pagesize": 50, "offset": %d}' % (self.qid, i*50)}
                r = post('http://www.zhihu.com/node/QuestionAnswerListV2', otherHeaders, data)
                for block in r.json()['msg']:
                    div = BeautifulSoup(block).div
                    if div.find('div', class_='answer-status') is not None:
                        continue  # 忽略建议修改的答案
                    self.answers.append(self._extractAnswer(div))

        return True

    def _extractAnswer(self, block):
        # aid
        aid = block['data-aid']
        # 回答人
        responderBlock = block.find('a', class_='zm-item-link-avatar')
        if responderBlock is None:
            responder = -1  # 匿名用户
        else:
            responder = responderBlock['href'][8:]  # /people/<responder>
        # 日期
        date = block['data-created']
        # 内容
        content = block.find('div', class_='zm-editable-content').text.strip()
        # 赞同数
        upvote = parseNum(block.find('span', class_='count').text)
        # 评论数目
        comments = block.find('a', class_='toggle-comment').text.strip()
        p = comments.find('条评论')
        if p > 0:
            commentsCount = int(comments[:p])
        else:
            commentsCount = 0

        answer = dict()
        answer['aid'] = aid
        answer['responder'] = responder
        answer['date'] = date
        answer['content'] = content
        answer['upvote'] = upvote
        answer['commentsCount'] = commentsCount
        return answer

    def toDict(self):
        dictResp = dict()
        dictResp['lastModified'] = self.lastModified
        dictResp['qid'] = self.qid
        dictResp['title'] = self.title
        dictResp['detail'] = self.detail
        dictResp['tags'] = self.tags
        dictResp['followersCount'] = self.followersCount
        dictResp['answers'] = self.answers
        return dictResp

    def __str__(self):
        return str(self.toDict())

    def persist(self, fp):
        json.dump(self.toDict(), fp, ensure_ascii=False)
