# zhihu_crawler
使用python 3实现的一个知乎内容的爬虫，依赖requests、BeautifulSoup4。

## 功能
* 爬取某话题下的所有问题列表

爬取内容：问题ID、问题标题、问题提出时间、问题来自的子话题
```python
from zhihu_crawler import zh_crawler

with open('questions_list.txt', 'a', encoding='utf8') as f:
    topic_id = 19550517  # 互联网话题ID
    zh_crawler.get_questions_list(topic_id, f, start_page=1, max_page=10)
```

* 爬取问题

爬取内容：问题ID、标题、内容、标签、提问者、所有回答（回答人、回答内容、回答时间、赞数）
```python
from zhihu_crawler import zh_crawler

question_id = 39051779
session = zh_crawler.get_login_session()
q = zh_crawler.get_question(session, question_id)
```
需要在config.json里填上用户名以及密码，登录时会用到（可能还会需要输入验证码）。

* 爬取答案的点赞者信息

爬取内容：点赞者ID、点赞者的赞同数, 感谢数, 提问数, 回答数信息
```python
from zhihu_crawler import zh_crawler

answer_id = 13148207
voters = zh_crawler.get_voters_profile(answer_id)
```
