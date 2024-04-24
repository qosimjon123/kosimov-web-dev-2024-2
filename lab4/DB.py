from flask import g
import mysql.connector
class MySQL:
    def __init__(self, app):
        self.app = app
        self.app.teardown_appcontext(self.close)

    def get_config(self):
        return {
            'host': self.app.config['MYSQL_DATABASE_HOST'],
            'user': self.app.config['MYSQL_DATABASE_USER'],
            'password': self.app.config['MYSQL_DATABASE_PASSWORD'],
            'database': self.app.config['MYSQL_DATABASE_DB']
        }

    def connect(self):
        if "db" not in g:
            g.db = mysql.connector.connect(**self.get_config())
            print("Connected to MySQL database")
        return g.db

    def close(self, exception=None):
        if "db" in g:
            g.db.close()
            g.pop("db", None)
            print("Disconnected from MySQL database")

    def query(self, sql, params=None, commit=False):
        try:
            if "db" not in g:
                g.db = self.connect()
            cursor = g.db.cursor(named_tuple=True)
            cursor.execute(sql, params)
            if commit:
                g.db.commit()
            res = cursor.fetchall()

            self.close()
            return res, True

        except Exception as e:
            print("Error executing query:", e)
            g.db.rollback()
            return None, False
