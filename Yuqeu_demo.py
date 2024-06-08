import requests
import sys
import json
import re
import os


def mkdir(path) -> None:
    path = path.strip().rstrip('\\')
    root = "Yuque"
    full_path = os.path.join(root, path)
    os.makedirs(full_path.encode('utf-8'), exist_ok=True)


def write(path, title, author, url, content) -> None:
    file_name = title + '.md'
    full_path = os.path.join('.\Yuque', author)
    try:
        with open(os.path.join(full_path, file_name), 'w', encoding='utf-8') as file:
            file.write(url + '  \n')
            file.write('作者：' + author + '  \n'+'---\n')
            file.write(content)
    except FileNotFoundError:
        pass


class yuque:

    def __init__(self, token: str):
        self.url = 'https://www.yuque.com/api/v2'  # 语雀公用路径开头
        self.header = {'X-Auth-Token': token}  # 团队token
        self.lib = self.get_libsData()  # 存储知识库数据

    def get_libsData(self) -> list[dict]:
        request = requests.get(self.url + '/user', headers=self.header)
        if request.status_code == 401:  # 如果无法访问，判断是token错误
            print("Token Wrong")
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
            res.append(doc)
        return res

    def update_time(self) -> bool:
        pass

    def get_docurl(self) -> str:
        pass

    def get_userDoc(self, users: list) -> None:
        for user in users:
            mkdir(user)
            for i in range(len(self.lib)):
                id = self.lib[i]['data']['id']
                doc = self.get_DocData(id, user)
                for j in range(len(doc)):
                    url = 'https://www.yuque.com/' + self.lib[i]['login'] + '/' + self.lib[i]['data']['slug'] + '/' + \
                          doc[j]['slug']
                    write(user, doc[j]['title'], user, url, doc[j]['content'])


if __name__ == '__main__':
    # token = input('input your token: ')
    token = 'sezlx7jnrr66IxweCelbFueNIkNrD3arAdPeFReD'
    yuque = yuque(token)
    user_name = ['阮一海']
    yuque.get_userDoc(user_name)
