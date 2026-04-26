import jwt
import datetime
import os

class TokenService:
    def __init__(self):
        self.secret = os.environ.get("JWT_SECRET", "segredo_padrao_para_teste")

    def generate_token(self, cpf: str) -> str:
        payload = {
            "sub": cpf,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            "iat": datetime.datetime.utcnow(),
            # ADICIONE ESTA LINHA PARA CASAR COM O TERRAFORM DO GATEWAY:
            "iss": "https://soat.techchallenge.com" 
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")