from unittest.mock import MagicMock
from src.core.use_cases import AuthenticateCustomer
from src.adapters.token_service import TokenService

def test_should_authenticate_valid_cpf():
    # Arrange
    # Use um CPF que passe na validação matemática (algoritmo mod11)
    valid_cpf = "52998224725" 

    # 1. Mock do TokenService (Simula a geração do token)
    # Não precisamos testar a lib jwt aqui, só queremos saber se ela foi chamada
    token_service = TokenService() 

    # 2. Mock do Repositório (Simula o Banco de Dados)
    # Aqui criamos um objeto falso que finge ter o método get_customer_status
    repo_mock = MagicMock()
    
    # Configuramos o mock para retornar um cliente "EXISTENTE" quando for chamado
    repo_mock.get_customer_status.return_value = {"exists": True, "status": "ATIVO"}

    # 3. Instancia o Caso de Uso injetando o Mock
    use_case = AuthenticateCustomer(token_service, repo_mock)

    # Act
    result, status = use_case.execute(valid_cpf)

    # Assert
    assert status == 200
    assert "access_token" in result
    
    # Verifica se o caso de uso realmente tentou chamar o banco de dados
    repo_mock.get_customer_status.assert_called_once()