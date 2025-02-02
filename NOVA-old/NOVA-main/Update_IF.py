import SQL_operation
import AI_summarize
import words_operation

import difflib
from datetime import timedelta
from dateutil import parser
import pytz



def get_time(timestamp):
    utc_datetime = parser.parse(timestamp)
    cst_timezone = pytz.timezone('Asia/Shanghai')
    return utc_datetime.astimezone(cst_timezone)


def fetch_update(now_article, record_article):
    now_article = now_article.replace('\\n', '\n')
    record_article = record_article.replace('\\n', '\n')

    diff = difflib.unified_diff(record_article.splitlines(keepends=False), now_article.splitlines(keepends=False),
                                fromfile='Before Update', tofile='After Update', lineterm='')
    added_content = []
    for line in diff:
        if line.startswith('+'):
            added_content.append(line[1:])

    return '\n'.join(added_content)


def check_freq(doc_info, text_data) -> bool:
    now_time = get_time(doc_info['doc_update_time'])
    record_time = get_time(text_data['update_time'])
    time_threshold = timedelta(minutes=10)
    if now_time - record_time < time_threshold:
        return False
    else:
        return True


def check_words(doc_info, text_data):
    update_text = fetch_update(doc_info['doc_content'], text_data['content'])
    words_threshold = 150
    if len(update_text) <= words_threshold:
        return False
    else:
        return True

def add_new(db_conn, doc_info, DB_config):
    doc_info['key_words'] = AI_summarize.summarize_keywords(doc_info['doc_content'])
    SQL_operation.INSERT(db_conn, DB_config, doc_info)


def check_update(db_conn, DB_config, doc_info):
    text_data = SQL_operation.SELECT(db_conn, DB_config, select_param='id=' + str(doc_info['doc_id']))
    text_data = SQL_operation.jsonify(db_conn, DB_config, text_data[0])
    if not check_freq(doc_info, text_data) or not check_words(doc_info, text_data):
        return
    else:
        doc_info['key_words'] = AI_summarize.summarize_keywords(doc_info['doc_content'])
        SQL_operation.UPDATE(db_conn, doc_info, DB_config, update_param='id=' + str(doc_info['doc_id']))
        update_text = fetch_update(doc_info['doc_content'], text_data['content'])
        new_topic = AI_summarize.summarize_new_topic(text_data['content'], update_text)

def notify_update():
    pass
