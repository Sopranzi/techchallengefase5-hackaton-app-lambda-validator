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
        self._schema_ready = False

    def get_connection(self):
        missing = [
            name for name, value in {
                "DB_HOST": self.host,
                "DB_NAME": self.database,
                "DB_USER": self.user,
                "DB_PASS": self.password,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Variaveis de banco ausentes na Lambda: {', '.join(missing)}")

        # Conexão com timeout curto para não estourar o tempo da Lambda
        print(f"[DB] Conectando em host={self.host} db={self.database} user={self.user} port={self.port}")
        conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
            connect_timeout=3
        )
        self.ensure_schema(conn)
        return conn

    def ensure_schema(self, conn):
        if self._schema_ready:
            return

        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id uuid PRIMARY KEY,
                    name varchar(255) NOT NULL,
                    document varchar(14) NOT NULL UNIQUE,
                    email varchar(255) NOT NULL UNIQUE,
                    password varchar(255),
                    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("ALTER TABLE customers ADD COLUMN IF NOT EXISTS password varchar(255)")
            cursor.execute("ALTER TABLE customers ADD COLUMN IF NOT EXISTS created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP")
            cursor.execute("ALTER TABLE customers ADD COLUMN IF NOT EXISTS updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP")
            cursor.execute("ALTER TABLE customers ADD COLUMN IF NOT EXISTS document varchar(14)")
            cursor.execute("ALTER TABLE customers ADD COLUMN IF NOT EXISTS email varchar(255)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS customers_document_uq ON customers (document)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS customers_email_uq ON customers (email)")
        conn.commit()
        self._schema_ready = True

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
