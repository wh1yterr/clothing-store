import psycopg2
from psycopg2 import Error

class DBConnector:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port="5432",
                database="clothingstoredb",
                user="postgres",
                password="12345"
            )
            self.cursor = self.conn.cursor()
            print("✅ Подключение к БД успешно")
        except Error as e:
            print(f"❌ Ошибка подключения: {e}")
            raise
    
    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params or [])
            self.conn.commit()
            return True
        except Error as e:
            print(f"❌ Ошибка выполнения: {e}")
            self.conn.rollback()
            return False
    
    def fetch(self, query, params=None):
        try:
            self.cursor.execute(query, params or [])
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ Ошибка чтения: {e}")
            return []
    
    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()