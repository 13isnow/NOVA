from Log import logger

import requests
import sys
import json
import re
import os

class YuqueBase:
    def __init__(self, token: str, save_path: str) -> None:
        self.save_path = save_path
        self.url = 'https://www.yuque.com/api/v2'  # 语雀公用路径开头
        self.header = {'X-Auth-Token': token}  # 团队token
        self.lib = self.get_libsData()  # 存储知识库数据

    def get_libsData(self) -> list[dict]:
        request = requests.get(self.url + '/user', headers=self.header)
        if request.status_code == 401:  # 如果无法访问，判断是token错误
            logger.error('token错误')
            sys.exit(0)

        user_info_dic = json.loads(request.text)
        login = user_info_dic['data']['login']  # 获取团队路径
        request = requests.get(self.url + '/users/' + login + '/repos', headers=self.header)
        blog_info_dic = json.loads(request.text)
        res = []
        for i in range(len(blog_info_dic['data'])):
            lib = dict()
            lib['login'] = login
            name = blog_info_dic['data'][i]['name']
            slug = blog_info_dic['data'][i]['slug']
            id = str(blog_info_dic['data'][i]['id'])
            # print("知识库\"{0}\"的id是：{1}".format(name, id))  # 打印id
            lib['data'] = {'name': name, 'slug': slug, 'id': id}  # 以字典形式记录
            res.append(lib)
        return res

    def get_DocData(self, id: str, name: str) -> list[dict]:
        request = requests.get(self.url + '/repos/' + id + '/docs', headers=self.header).text
        posts_info_dict = json.loads(request)
        res = []
        for i in range(len(posts_info_dict['data'])):
            doc = dict()
            if posts_info_dict['data'][i]['type'] != 'Doc' or posts_info_dict['data'][i]['user']['name'] != name:
                continue

            doc['title'] = posts_info_dict['data'][i]['title']
            doc['slug'] = posts_info_dict['data'][i]['slug']
            doc['publish_time'] = posts_info_dict['data'][i]['published_at']
            request = requests.get(self.url + '/repos/' + id + '/docs/' + doc['slug'], headers=self.header).text
            posts_test_dict = json.loads(request)
            posts_text = posts_test_dict['data']['body']
            posts_text = re.sub(r'\\n', "\n", posts_text)
            doc['content'] = posts_text
            if doc['content'] == '':
                continue
            res.append(doc)
        return res

    def update_time(self) -> bool:
        pass

    def get_docurl(self) -> str:
        pass
    
    def is_update(self, doc, doc_path) -> bool:
        if not os.path.exists(doc_path):
            return True
        with open(doc_path, 'r', encoding='utf-8') as file:
            try:
                lines = file.readlines()
                if doc['publish_time'] in lines[0]:
                    return False
                return True
            except Exception:
                print(lines)
                print(doc['publish_time'])

    def get_userDoc(self, users: list) -> None:
        for user in users:
            userdoc_dir = self.mkdir(user)
            for i in range(len(self.lib)):
                id = self.lib[i]['data']['id']
                docs = self.get_DocData(id, user)
                for j in range(len(docs)):
                    doc_path = os.path.join(userdoc_dir, docs[j]['title'] + f'-{id}' + '.md')
                    if self.is_update(docs[j], doc_path):
                        url = 'https://www.yuque.com/' + self.lib[i]['login'] + '/' + self.lib[i]['data']['slug'] + '/' + docs[j]['slug']
                        self.write(doc_path, user, url, docs[j]['content'], docs[j]['publish_time'])

            logger.info(f"{user} doc download success")

    def mkdir(self, path) -> None:
        path = path.strip().rstrip('\\')
        full_path = os.path.join(self.save_path, path)
        os.makedirs(full_path.encode('utf-8'), exist_ok=True)
        return full_path

    def write(self, full_path, author, url, content, update_time) -> None:
        try:
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write('publish time: ' + update_time + '  \n')
                file.write(url + '  \n')
                file.write('author: ' + author + '  \n'+'---\n')
                file.write(content)
        except FileNotFoundError:
            logger.error(f"FileNotFoundError: {full_path}")
