import psycopg2
from psycopg2 import pool
import logging

class DatabaseManager:
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool

    def execute_query(self, query, params=None):
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                else:
                    result = None
                    conn.commit()
                logging.debug(f"Executing query: {query}")
                logging.debug(f"Query parameters: {params}")
                logging.debug(f"Query result: {result}")
                return result
        except Exception as e:
            logging.error(f"Database error: {e}")
            return None
        finally:
            self.connection_pool.putconn(conn)