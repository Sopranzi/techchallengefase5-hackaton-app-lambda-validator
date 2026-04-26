import os
import jwt

def lambda_handler(event, context):
    """
    Authorizer para HTTP API com resposta simples.
    Retorna isAuthorized/context em vez de policy IAM para evitar 500 no API Gateway.
    """
    token = event.get("headers", {}).get("authorization", "") or event.get("headers", {}).get("Authorization", "")

    if token.lower().startswith("bearer "):
        token = token[7:]

    if not token:
        return {"isAuthorized": False}

    try:
        secret = os.environ["JWT_SECRET"]
        payload = jwt.decode(token, secret, algorithms=["HS256"], issuer="https://soat.techchallenge.com")

        return {
            "isAuthorized": True,
            "context": {
                "sub": payload.get("sub", ""),
                "role": payload.get("role", "")
            }
        }
    except jwt.ExpiredSignatureError:
        print("Token expirado")
        return {"isAuthorized": False}
    except jwt.InvalidTokenError as e:
        print(f"Token inválido: {str(e)}")
        return {"isAuthorized": False}
    except Exception as e:
        print(f"Erro interno no authorizer: {str(e)}")
        return {"isAuthorized": False}
