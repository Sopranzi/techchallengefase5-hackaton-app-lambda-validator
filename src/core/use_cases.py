from src.core.entities import Cpf
from src.adapters.token_service import TokenService
from src.adapters.customer_repository import CustomerRepository

class AuthenticateCustomer:
    def __init__(self, token_service: TokenService, customer_repo: CustomerRepository):
        self.token_service = token_service
        self.customer_repo = customer_repo

    def execute(self, cpf_input: str):
        # 1. Valida CPF
        try:
            cpf = Cpf(cpf_input)
        except ValueError:
            return {"error": "CPF Inválido"}, 400 # Retorna tupla

        # 2. Consulta Banco
        try:
            customer_data = self.customer_repo.get_customer_status(cpf.value)
        except Exception as e:
            print(f"Erro no repo: {e}")
            return {"error": "Erro interno ao consultar base de dados"}, 500 # Retorna tupla

        if not customer_data["exists"]:
            return {"error": "Cliente não cadastrado"}, 404 # Retorna tupla

        # 3. Gera Token
        token = self.token_service.generate_token(cpf.value)
        
        # 4. Sucesso
        return {
            "access_token": token,
            "token_type": "Bearer",
            "customer_status": customer_data["status"]
        }, 200 # Retorna tupla (dict, int)