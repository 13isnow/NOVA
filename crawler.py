import requests
from bs4 import BeautifulSoup
import time


# 借鉴借鉴翔宇同学的封装，我就暂时懒得分文件了
class CrawlerData:

    def __init__(self, web_addr, **kwargs):
        self.url = web_addr
        self.response = self.get(**kwargs)
        self.soup = self.get_soup()

    def __del__(self):
        del self

    def get(self, **kwargs):
        try:
            if 'headers' in kwargs and 'params' in kwargs:
                res = requests.get(self.url, headers=kwargs['headers'], params=kwargs['params'])
            else:
                res = requests.get(self.url)
            if res.ok:
                return res
            else:
                raise AssertionError
        except (requests.exceptions.SSLError, AssertionError):
            print('Crawler.get: ' + self.url + "未响应")
            return None

    def get_soup(self, encoding='utf-8'):
        if self.response is None:
            return None
        self.response.encoding = 'utf-8'
        return BeautifulSoup(self.response.text, 'html.parser')


class Crawler(CrawlerData):

    def __init__(self, web_addr, **kwargs):
        super(Crawler, self).__init__(web_addr, **kwargs)
        self.url_set = self.get_google_url()

    def get_google_url(self):
        result = self.soup.find_all('a')
        url_set = set()
        for urls in result:
            url = urls.get('href')
            # 按理来说我应该用正则表达式的
            # 但可惜我不太熟练，只能用下标索引的方式应付一下
            index1 = url.find('&sa')
            index2 = url.find('http')
            if index1 > 0 and index2 >= 0:
                url = url[index2: index1]
                url_set.add(url)
        return url_set

    def get_google_content(self, path):
        with open(path, 'r') as file:
            for url in self.url_set:
                crawler_data = CrawlerData(url)
                content = crawler_data.soup.find_all('p')
                for seg in content:
                    if seg != '\n':
                        file.write(seg)


if __name__ == '__main__':
    for i in range(0, 110, 10):
        web_url = f"https://www.google.com/search?q=%E7%A8%8B%E5%BC%80%E7%94%B2&sca_esv=600400644&sxsrf=ACQVn09spxgLQI1voAvTOKlB9WQ_MN6c0Q:1705932986833&ei=uniuZcm6MpPg2roP6uqI4AI&start={i}&sa=N&biw=601&bih=632&dpr=1.5"
        crawler = Crawler(web_url)
        crawler.get_google_content('data.txt')
        time.sleep(3)
