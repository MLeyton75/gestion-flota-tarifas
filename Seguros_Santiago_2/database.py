import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Conectar a la base de datos MySQL"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host='localhost',
                    database='seguros_santiago_2',
                    user='root',
                    password='Marce_75',
                    autocommit=True  # 👈 habilitamos autocommit para evitar problemas
                )
                logger.info("✅ Conexión a MySQL exitosa")
            return self.connection
        except Error as e:
            logger.error(f"❌ Error conectando a MySQL: {e}")
            return None
    
    def disconnect(self):
        """Cerrar la conexión con la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("🔌 Conexión a MySQL cerrada")
            self.connection = None
    
    def execute_query(self, query, params=None, fetch=True, one=False):
        """
        Ejecutar consultas SQL con manejo de errores.
        :param query: SQL query
        :param params: parámetros de la query
        :param fetch: True si se requiere fetch
        :param one: True si se espera un solo resultado
        :return: dict | list | bool
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            result = None
            if fetch:
                if query.strip().upper().startswith("SELECT"):
                    if one:
                        result = cursor.fetchone()  # 👈 trae solo un registro
                    else:
                        result = cursor.fetchall()
                else:
                    result = cursor.rowcount > 0
            else:
                result = True

            cursor.close()
            return result

        except Error as e:
            logger.error(f"❌ Error en consulta SQL: {e}")
            logger.error(f"   Query: {query}")
            logger.error(f"   Params: {params}")
            return False
        except Exception as e:
            logger.error(f"⚠️ Error inesperado: {e}")
            return False
