import re

class Cpf:
    def __init__(self, value: str):
        if not self._validate(value):
            raise ValueError("CPF Inválido")
        self.value = re.sub(r'\D', '', value)

    def _validate(self, cpf: str) -> bool:
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Cálculo dos dígitos verificadores (Simplificado para brevidade)
        for i in range(9, 11):
            val = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
            digit = ((val * 10) % 11) % 10
            if digit != int(cpf[i]):
                return False
        return True