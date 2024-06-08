import os
import sys
import mysql.connector
from mysql.connector import Error


def DocPath():
    directory_path = ".\\YUQUE\\"
    res = []
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            path = dict()
            path['author'] = os.path.basename(root)
            path['title'] = os.path.splitext(filename)[0]
            path['path'] = os.path.join(root, filename)
            res.append(path)
    return res


class SQL:
    def __init__(self, config, instructions):
        self.config = config
        self.instructions = instructions
        self.cursor = self.connect(config)

    def __del__(self):
        if self.cursor.is_connected():
            self.cursor.close()
            print("MySQL connection is closed")

    def connect(self, config):
        try:
            connection = mysql.connector.connect(**config)
            print("Connected to MySQL server")
            return connection
        except Error as e:
            print("Error while connecting to MySQL", e)
            sys.exit(0)

    def createDB(self):
        create_db_query = """
        CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """.format(self.instructions['database'])

        try:
            with self.cursor.cursor() as cursor:
                cursor.execute(create_db_query)
                print("Database created successfully")
        except Error as e:
            print("Error creating database", e)
            sys.exit(0)

    def useDB(self):
        use_database_query = '''USE {};'''.format(self.instructions['database'])
        try:
            with self.cursor.cursor() as cursor:
                cursor.execute(use_database_query)
        except Error as e:
            print("Error Using database", e)

    def createTable(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS {} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                author VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                path VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """.format(self.instructions['table'])
        try:
            with self.cursor.cursor() as cursor:
                cursor.execute(create_table_query)
                print("Table created successfully")
        except Error as e:
            print("Error creating table", e)

    def insertData(self):
        insert_data = DocPath()
        insert_query = "INSERT INTO {} (author, title, path) VALUES (%s, %s, %s)".format(self.instructions['table'])
        try:
            with self.cursor.cursor() as cursor:
                for file in insert_data:
                    cursor.execute(insert_query, (file['author'], file['title'], file['path']))
            self.cursor.commit()
            print("Data imported successfully")
        except Error as e:
            print("Error importing data", e)
            sys.exit(0)

    def showData(self):
        show_query = "SELECT * FROM {}".format(self.instructions['table'])
        try:
            with self.cursor.cursor() as cursor:
                cursor.execute(show_query)
                data = cursor.fetchall()
                for row in data:
                    print(row)
        except Error as e:
            print("Error showing data", e)
            sys.exit(0)

    def DelAllData(self):
        del_query = "TRUNCATE TABLE {};".format(self.instructions['table'])
        try:
            with self.cursor.cursor() as cursor:
                cursor.execute(del_query)
                self.cursor.commit()
                print("Table deleted successfully")
        except Error as e:
            print("Error deleting", e)
            sys.exit(0)


def main():
    config = {
        'user': 'root',
        'password': 'ryh20030916',
        'host': 'localhost',
    }

    instructions = {
        'database': 'Nova',
        'table': 'test'
    }

    mySQL = SQL(config, instructions)
    mySQL.createDB()
    mySQL.useDB()
    mySQL.createTable()
    mySQL.DelAllData()
    mySQL.insertData()
    mySQL.showData()


if __name__ == "__main__":
    main()
