import psycopg2
import json
from datetime import datetime, timedelta
from searchapp.config.config import postgresdb_config
from collections import OrderedDict
import time

class user_model():

    def __init__(self):
        postgres_connection_string = f"postgresql://{postgresdb_config['username']}:{postgresdb_config['password']}@{postgresdb_config['host']}:{postgresdb_config['port']}/{postgresdb_config['database']}" ##
        self.conn = psycopg2.connect(postgres_connection_string) ##
        self.conn.autocommit = True
        #self.cur = self.conn.cursor(dictionary=True)
        self.cache = OrderedDict()
        self.MAX_CACHE_SIZE = 1000
        self.DEFAULT_CACHE_TTL = 3600

    def get_popular_users(self):
        try:
            cursor = self.conn.cursor()
            sql_query = """
                SELECT *
                FROM users
                ORDER BY followers_count DESC, friends_count DESC, favourites_count DESC
                LIMIT 10; 
            """
            cursor.execute(sql_query)
            popular_users = cursor.fetchall()
            cursor.close()

            return popular_users

        except psycopg2.Error as e:
            print("Error fetching popular users:", e)
            return None

    def get_user_metadata(self, name=None, userid=None):
        try:
            cursor = self.conn.cursor()
            if name:
                sql_query = """
                    SELECT *
                    FROM users
                    WHERE lower(name) LIKE %s;
                """
                cursor.execute(sql_query, ('%' + name + '%',))
            elif userid:
                sql_query = """
                    SELECT *
                    FROM users
                    WHERE id_str = %s;
                """
                cursor.execute(sql_query, (userid,))
            else:
                print("User information not available")
                cursor.close()
                return None
            user_metadata = cursor.fetchall()
            cursor.close()

            return user_metadata

        except psycopg2.Error as e:
            print("Error fetching user metadata:", e)
            return None