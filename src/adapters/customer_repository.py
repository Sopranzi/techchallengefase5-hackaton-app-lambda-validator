import os
import uuid
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

class CustomerRepository:
    def __init__(self):
        self.host = os.environ.get("DB_HOST")
        self.database = os.environ.get("DB_NAME")
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASS")
        self.port = int(os.environ.get("DB_PORT", 5432))

    def get_connection(self):
        # Conexão com timeout curto para não estourar o tempo da Lambda
        print(f"[DB] Conectando em host={self.host} db={self.database} user={self.user} port={self.port}")
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
            connect_timeout=3
        )

    def get_customer_by_cpf(self, cpf: str):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT document, password FROM customers WHERE document = %s"
                cursor.execute(query, (cpf,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print(f"Erro ao buscar cliente: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    def create_customer(self, cpf: str, password: str = None, name: str = None, email: str = None):
        conn = None
        try:
            conn = self.get_connection()
            
            new_id = str(uuid.uuid4())
            # Usando utcnow para garantir compatibilidade com OffsetDateTime
            now = datetime.datetime.utcnow() 
            
            final_name = name if name else f"Cliente {cpf}"
            final_email = email if email else f"{cpf}@email.com"

            with conn.cursor() as cursor:
                query = """
                    INSERT INTO customers 
                    (id, name, document, email, password, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    new_id, 
                    final_name, 
                    cpf, 
                    final_email,
                    password, 
                    now, 
                    now
                ))
                conn.commit()
                return True, None
                
        except Exception as e:
            print(f"Erro ao criar cliente: {str(e)}")
            if conn:
                conn.rollback()
            return False, str(e)
            
        finally:
            if conn:
                conn.close()
