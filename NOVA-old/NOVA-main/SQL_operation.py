import sys
import mysql.connector
from mysql.connector import Error


def db_connect(config):
    try:
        db_conn = mysql.connector.connect(**config)
        print("Connected to MySQL server")
        return db_conn
    except Error as e:
        print("Error while connecting to MySQL", e)
        sys.exit(0)


def jsonify(db_conn, DB_config, data):
    column_names = DESCRIBE(db_conn, DB_config)
    result = dict()
    for i in range(len(column_names)):
        result[column_names[i]] = data[i]
    return result


def UPDATE(db_conn, doc_info, DB_config, update_param):
    cursor = db_conn.cursor()
    USE(db_conn, cursor, DB_config)
    update_query = f"UPDATE {DB_config['TABLE']}  SET id=%s, title=%s, update_time=%s, key_words=%s, content=%s WHERE {update_param};"
    cursor.execute(update_query, (
        doc_info['doc_id'], doc_info['doc_title'], doc_info['doc_update_time'], doc_info['key_words'],
        doc_info['doc_content']))
    db_conn.commit()
    print('update success')
    cursor.close()


def INSERT(db_conn, DB_config, doc_info):
    cursor = db_conn.cursor()
    USE(db_conn, cursor, DB_config)
    insert_query = f"INSERT INTO {DB_config['TABLE']} (id, title, update_time, key_words, content) VALUES (%s, %s, %s, %s, %s) ;"
    cursor.execute(insert_query, (
        doc_info['doc_id'],
        doc_info['doc_title'],
        doc_info['doc_update_time'],
        doc_info['key_words'],
        doc_info['doc_content']
    )
                   )
    db_conn.commit()
    print('insert success')
    cursor.close()


def SHOW(db_conn, cursor, DB_config):
    show_query = f"SELECT * FROM {DB_config['TABLE']}"
    cursor.execute(show_query)
    db_conn.commit()
    print(cursor.fetchall())


def USE(db_conn, cursor, DB_config):
    use_query = f"USE {DB_config['DATABASE']};"
    cursor.execute(use_query)
    db_conn.commit()


def SELECT(db_conn, DB_config, select_param):
    cursor = db_conn.cursor()
    USE(db_conn, cursor, DB_config)
    select_query = f"SELECT * FROM {DB_config['TABLE']} WHERE {select_param};"
    cursor.execute(select_query)
    result = cursor.fetchall()
    cursor.close()
    return result


def DESCRIBE(db_conn, DB_config):
    cursor = db_conn.cursor()
    describe_query = f"DESCRIBE {DB_config['TABLE']};"
    cursor.execute(describe_query)
    columns_info = cursor.fetchall()
    column_names = [column[0] for column in columns_info]
    db_conn.commit()
    cursor.close()
    return column_names
