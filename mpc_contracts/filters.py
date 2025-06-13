from .globalvars import G
from .models import Contract
from .validators import validate_cpf
from datetime import datetime as dt, timedelta
from django_filters import FilterSet, CharFilter
from rest_framework.exceptions import ValidationError

class ContractFilter(FilterSet):
    contract_date = CharFilter(method='filter_contract_date')
    customer_cpf = CharFilter(method='filter_customer_cpf')
    customer_state = CharFilter(method='filter_customer_state')

    class Meta:
        model = Contract
        fields = ['contract_id','customer_cpf','contract_date','customer_state']

    ##──── Faz validação/normalização antes para não onerar o backend de dados com pesquisas inválidas ────────────────────────────────────────────
    def filter_customer_cpf(self, queryset, name, value):
        try:
            cpf = validate_cpf(value)
        except ValidationError as ERR:
            raise ValidationError(f"Invalid customer_cpf provided: {value}")
        return queryset.filter(**{name:cpf})

    def filter_customer_state(self, queryset, name, value):
        uf = value.upper().strip()
        if len(uf) != 2:
            raise ValidationError("Invalid customer_state code. Must be exactly 2 characters long")
        elif not uf.isalpha():
            raise ValidationError("Invalid customer_state code. State code must contain only alphabetic characters")
        elif uf not in G.UF_LIST:
            raise ValidationError(f"Invalid customer_state code: {uf}. Must be one of {str(list(G.UF_LIST.keys())).replace(' ','')[1:-1]}")
        return queryset.filter(**{name:uf})

    def filter_contract_date(self, queryset, name, value):
        try:
            # print(value,name)
            # print(queryset)
            value = value.strip()[:10] # mesmo que forneçam data/hora, vamos considerar somente a data
            if len(str(value)) == 4:     # somente por ano
                ##──── monta um range com o primeiro e último dia do ano 
                first_day = dt.strptime(str(value),"%Y").date().replace(month=1,day=1)
                last_day = first_day.replace(month=12,day=31)
                # print(first_day,last_day)
                return queryset.filter(contract_date__range=(first_day,last_day))
            elif len(str(value)) == 7:   # por ano e mês
                ##──── monta um range com o primeiro e último dia do mês
                date_obj = dt.strptime(str(value),"%Y-%m")
                first_day = date_obj.replace(day=1)
                last_day = first_day + timedelta(days=31)
                last_day = last_day.replace(day=1) - timedelta(days=1)
                # print(first_day,last_day)
                return queryset.filter(contract_date__range=(first_day,last_day))
            elif len(str(value)) == 10:    # data completa
                date_obj = dt.strptime(str(value),"%Y-%m-%d").date()
                return queryset.filter(contract_date=date_obj)
            else:
                raise ValidationError(f"Invalid contract_date format: {value}. Expected formats: YYYY, YYYY-MM, or YYYY-MM-DD.")
        except ValueError: # Se a data for invalida ou ocorrer qualquer erro
            raise ValidationError(f"Invalid contract_date format: {value}. Expected formats: YYYY, YYYY-MM, or YYYY-MM-DD.")