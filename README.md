# zhihu_crawler
使用python 3实现的一个知乎内容的爬虫，依赖requests、BeautifulSoup4。

## 功能
能够爬取以下内容：
* 对于“问题”：标题、内容、关注人数、所在标签、所有回答（回答人、回答内容、赞数以及评论数）
* 对于“用户”：提问数量、回答数量、获得的总赞数、被关注人数、关注的话题、关注的人

## 使用方法
需要在config.json里填上用户名以及密码，当程序运行时，登录时可能会需要输入验证码。

* 对于“问题”
```python
from zhihu_question import Question

qid = <qid>  # 问题id
q = Question(qid)
q.update()  # 获取信息
q.persist(open(str(qid)+'.json', 'w', encoding='utf-8'))  # 以json的格式存储下来
```
* 对于“用户”
```python
from zhihu_person import Person

pid = 'liu-peng-cheng-sai-l'
p = Person(pid)
p.update()
p.persist(open(str(pid)+'.json', 'w', encoding='utf-8'))  # 以json的格式存储下来
```
