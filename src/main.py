import json
import os
import datetime
import re
import jwt
from src.adapters.customer_repository import CustomerRepository

# --- Funções Auxiliares ---

def clean_cpf_str(cpf: str) -> str:
    """Remove caracteres não numéricos do CPF."""
    return re.sub(r'\D', '', cpf)

def validate_cpf_format(cpf: str) -> bool:
    """Valida formato básico: 11 dígitos e não repetidos."""
    clean = clean_cpf_str(cpf)
    if len(clean) != 11 or len(set(clean)) == 1:
        return False
    return True

# --- Serviço de Autenticação ---

class AuthService:
    def __init__(self):
        self.repository = CustomerRepository()
        self.secret = os.environ.get("JWT_SECRET", "default_secret")
        self.issuer = "https://soat.techchallenge.com"

    def authenticate(self, body):
        raw_cpf = body.get("cpf") or body.get("document")
        password_input = body.get("password")

        if not raw_cpf:
            print("[AUTH] CPF ausente no payload")
            return {"statusCode": 400, "body": json.dumps({"error": "CPF é obrigatório"})}

        cpf = clean_cpf_str(raw_cpf)

        if not validate_cpf_format(cpf):
            print(f"[AUTH] CPF inválido format={raw_cpf} clean={cpf}")
            return {"statusCode": 400, "body": json.dumps({"error": "CPF inválido"})}

        # Busca no banco
        print(f"[AUTH] Buscando cliente cpf={cpf}")
        customer = self.repository.get_customer_by_cpf(cpf)

        if not customer:
            print(f"[AUTH] Cliente não encontrado cpf={cpf}")
            return {"statusCode": 404, "body": json.dumps({"error": "Cliente não encontrado"})}

        user_role = "client"

        # LÓGICA DE DECISÃO DE ROLE
        # Cenário 1: Admin (enviou senha e ela bate com o banco)
        if password_input:
            db_password = customer.get("password")
            print(f"[AUTH] Password informado. Comparando... cpf={cpf}")
            if db_password == password_input:
                user_role = "admin"
            else:
                print(f"[AUTH] Senha incorreta cpf={cpf}")
                return {"statusCode": 401, "body": json.dumps({"error": "Senha incorreta"})}
        
        # Cenário 2: Cliente (não enviou senha, mas CPF existe)
        else:
            user_role = "client"

        # Gera token
        print(f"[AUTH] Gerando token cpf={cpf} role={user_role}")
        token = self.generate_token(cpf, user_role)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "access_token": token,
                "role": user_role,
                "expires_in": 1800
            })
        }

    def signup(self, body):
        raw_cpf = body.get("cpf") or body.get("document")
        password = body.get("password")
        name = body.get("name")
        email = body.get("email")

        if not raw_cpf:
            print("[SIGNUP] CPF ausente no payload")
            return {"statusCode": 400, "body": json.dumps({"error": "CPF é obrigatório"})}

        cpf = clean_cpf_str(raw_cpf)
        
        if not validate_cpf_format(cpf):
            print(f"[SIGNUP] CPF inválido format={raw_cpf} clean={cpf}")
            return {"statusCode": 400, "body": json.dumps({"error": "CPF inválido"})}

        # Captura o sucesso E a mensagem de erro detalhada
        print(f"[SIGNUP] Inserindo cpf={cpf} name={name} email={email}")
        success, error_message = self.repository.create_customer(cpf, password, name, email)
        
        if success:
            print(f"[SIGNUP] Sucesso cpf={cpf}")
            return {
                "statusCode": 201, 
                "body": json.dumps({"message": "Cliente cadastrado com sucesso!"})
            }
        else:
            # Retorna o erro exato do banco de dados para debugging
            print(f"[SIGNUP] Falha cpf={cpf} err={error_message}")
            return {
                "statusCode": 500, # Mudando para 500 para indicar erro de execução
                "body": json.dumps({
                    "error": "Falha ao cadastrar no banco.",
                    "db_details": error_message # AQUI ESTÁ A RESPOSTA QUE PRECISAMOS
                })
            }

    def generate_token(self, cpf: str, role: str) -> str:
        payload = {
            "sub": cpf,
            "role": role, # 'admin' ou 'client'
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            "iat": datetime.datetime.utcnow(),
            "iss": self.issuer
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

# --- Handler Principal (Ponto de Entrada da Lambda) ---

def lambda_handler(event, context):
    try:
        body_str = event.get("body", "{}")
        if not body_str:
            return {"statusCode": 400, "body": json.dumps({"error": "Body vazio"})}
            
        # Tratamento para quando o body já vem como dict (testes locais) ou string (API Gateway)
        if isinstance(body_str, str):
            body = json.loads(body_str)
        else:
            body = body_str
        print(f"[REQUEST] body={body}")
            
        service = AuthService()

        # ROTEAMENTO
        if body.get("action") == "signup":
            return service.signup(body)
        else:
            return service.authenticate(body)

    except Exception as e:
        print(f"Erro critico: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Erro interno no servidor"})
        }
