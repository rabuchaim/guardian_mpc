from .globalvars import G
from rest_framework import serializers

__all__ = ['validate_uf_code', 'validate_cpf']

def validate_uf_code(value)->str:
    """Validate if the provided UF code is valid."""
    uf_code = value.strip().upper()
    if len(uf_code) != 2:
        raise serializers.ValidationError("Invalid UF code: must be exactly 2 characters long")
    elif uf_code not in G.UF_LIST:
        raise serializers.ValidationError(f"Invalid UF code: {uf_code}. Must be one of {str(list(G.UF_LIST.keys())).replace(' ','')[1:-1]}")
    return uf_code 

def validate_cpf(value)->str:
    """Validate if the provided CPF is valid."""
    def calc_dv(digitos):
        soma = sum(int(dig)*peso for dig,peso in zip(digitos,range(len(digitos)+1,1,-1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11-resto)
    
    cpf = ''.join(filter(str.isdigit,value.strip()))
    if len(cpf) != 11:
        raise serializers.ValidationError("Invalid CPF: must contain 11 numeric digits") from None
    elif cpf == cpf[0] * 11:
        raise serializers.ValidationError("Invalid CPF: all digits are the same") from None
    dv1 = calc_dv(cpf[:9])
    dv2 = calc_dv(cpf[:9]+dv1)
    if cpf[-2:] != dv1+dv2:
        raise serializers.ValidationError("Invalid CPF") from None
    return cpf 
