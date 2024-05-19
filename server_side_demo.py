import SQL_operation
import Update_IF
from send_email import Email_operation

from flask import Flask, request, jsonify
import time

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    process_data(data)
    return jsonify({"message": "Webhook received"})


class config_set:
    SQL_config = {
        'user': 'ryh',
        'password': '12345678',
        'host': 'localhost',
    }

    DB_config = {
        'DATABASE': 'test_base',
        'TABLE': 'test_table',
    }

    emailSender_config = {
        'name': '阮一海',
        'email': '231300059@smail.nju.edu.cn',
        'token': 'CtJiUTg68y3HopWd',
        'host': "smtp.nju.edu.cn"
    }


def process_data(data):
    if data['data']["action_type"] == "comment_create":
        process_comment(data)
    if data['data']["action_type"] == "publish":
        if data['data']['format'] == 'lake':
            process_doc(data)

    print('get one message.')


def process_comment(data):
    def get_info() -> dict:
        nonlocal data
        info = dict()
        info['subject'] = '叮~ 语雀评论提醒'
        info['create_time'] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        info['commenter'] = data['data']['user']['name']
        info['author_id'] = data['data']['commentable']['user_id']
        info['title'] = data['data']['commentable']['title']
        info['content'] = data['data']['body_html']

        return info

    comment_info = get_info()
    Email_operation.send_comment(Email_operation(config_set.emailSender_config), comment_info)


def process_doc(data):
    def get_info() -> dict:
        nonlocal data
        info = dict()
        info['doc_url'] = data['data']['url']
        info['doc_id'] = data['data']['id']
        info['doc_title'] = data['data']['title']
        info['doc_update_time'] = data['data']['published_at']
        info['doc_content'] = data['data']['body']
        # doc_info['doc_user_id'] = data['data']['user']['user_id']
        info['key_words'] = 'None'
        return info

    def if_exist() -> bool:
        nonlocal db_conn, doc_info
        result = False
        if SQL_operation.SELECT(db_conn, config_set.DB_config, select_param='id=' + str(doc_info['doc_id'])):
            result = True

        return result

    doc_info = get_info()
    db_conn = SQL_operation.db_connect(config=config_set.SQL_config)
    if not if_exist():
        Update_IF.add_new(db_conn, doc_info, config_set.DB_config)
        db_conn.close()
        return

    Update_IF.check_update(db_conn, config_set.DB_config, doc_info)
    db_conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
