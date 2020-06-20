import psycopg2
import configparser


class DbContext:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('app/config.ini')

        self.conn = psycopg2.connect(
            dbname=self.config['DB']['dbname'],
            user=self.config['DB']['user'],
            # password=self.config['DB']['password'],
            host=self.config['DB']['host'],
            port=self.config['DB']['port']
        )
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def select(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()
