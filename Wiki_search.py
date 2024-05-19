import wikipedia
from zhconv import convert
import jieba.posseg as pseg
from textrank4zh import TextRank4Keyword

"""
pip install wikipedia
pip install zhconv
pip install jieba
pip install textrank4zh
"""


def convert_zh(text, aim='zh-hans'):
    """
    因为某些众说周知的原因，Wiki接口只能调取繁体中文的网站
    所以需要自己做繁简转换，这里选用了一个轻量级简繁转换项目zhconv，没用使用较为正式的OpenCC库
    """
    return convert(text, aim)


def Wiki_links(search_term, language='zh'):
    wikipedia.set_lang(language)

    try:
        text = wikipedia.page(search_term)
        return [convert(i, 'zh-hans') for i in text.links]
    except wikipedia.exceptions.DisambiguationError as e:
        return []


def Wiki_summary(search_term, language='zh'):
    wikipedia.set_lang(language)
    return wikipedia.summary(search_term)


def load_stopwords(stopwords_file_path):
    stopwords = set()
    with open(stopwords_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stopwords.add(line.strip())
    return stopwords


def filter_documents(text, stopwords):
    document = []
    words = pseg.cut(text.strip())
    for word, flag in words:
        if flag.startswith('n') and word not in stopwords and len(word) > 1:
            document.append(word)
    return document


def textrank(document, top_n=10):
    tr4w = TextRank4Keyword()
    text = ' '.join(document)
    tr4w.analyze(text=text, lower=True, window=2)
    keywords = tr4w.get_keywords(top_n, word_min_len=2)
    return [keyword.word for keyword in keywords]


def extract_keywords(stopwords_file_path, search_term):
    stopwords = load_stopwords(stopwords_file_path)
    document = Wiki_summary(search_term)
    top_keywords = textrank(filter_documents(document, stopwords))
    top_keywords = [convert_zh(word) for word in top_keywords]
    print(top_keywords)
