import random
import math
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime as dt
# dateutil.relativedelta trabalha com meses reais, respeita fevereiro com 28/29 dias e meses com 30/31 dias
from dateutil.relativedelta import relativedelta 
from .models import Contract, Parcel
from .globalvars import G

def generate_random_cpf(formatted:bool=True)->str:
    """Generate a random valid CPF."""
    def calc_dv(digitos):
        soma = sum(int(dig)*peso for dig,peso in zip(digitos,range(len(digitos)+1,1,-1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11-resto)    
    cpf = [str(random.randint(0,9)) for _ in range(9)]
    dv1 = calc_dv(cpf)
    dv2 = calc_dv(cpf+[dv1])
    if formatted: # xxx.xxx.xxx-xx
        return f"{''.join(cpf[:3])}.{''.join(cpf[3:6])}.{''.join(cpf[6:9])}-{dv1}{dv2}"
    return ''.join(cpf)+dv1+dv2

def get_a_random_state_code()->str:
    """Get a random valid Brazilian state code."""
    return random.choice(list(G.UF_LIST.keys()))

class ContractsTestCase(APITestCase):
    def setUp(self):
        self.max_parcels = 5
        self.contract_data = {
                "contract_date":"2025-06-09",
                "contract_amount":2000,
                "contract_rate":1.5,
                "customer_cpf":generate_random_cpf(),
                "customer_birth_date":"1976-10-26",
                "customer_country":"Brasil",
                "customer_state":"SP",
                "customer_city":"São Paulo",
                "customer_phone":"16997228598"
            }
        parcel_amount = math.trunc(((self.contract_data['contract_amount']*self.contract_data['contract_rate'])/self.max_parcels)*100)/100
        self.contract_data['parcels'] = []
        for I in range(self.max_parcels):
            self.contract_data['parcels'].append({
                    "parcel_number":I+1,"parcel_amount":parcel_amount,
                    "parcel_due_date":(dt.strptime(str(self.contract_data['contract_date']),"%Y-%m-%d").date() + relativedelta(months=I+1)).strftime('%Y-%m-%d')
                }
            )
        self.contract_data_bulk = [
            {
                "contract_date":"2024-12-01",
                "contract_amount":14000,
                "contract_rate":1.5,
                "customer_cpf":generate_random_cpf(),
                "customer_birth_date":"1976-10-26",
                "customer_country":"Brasil",
                "customer_state":"SC",
                "customer_city":"Florianópolis",
                "customer_phone":"16997228598"
            },            
            {
                "contract_date":"2025-06-09",
                "contract_amount":12000,
                "contract_rate":1.5,
                "customer_cpf":generate_random_cpf(),
                "customer_birth_date":"1976-10-26",
                "customer_country":"Brasil",
                "customer_state":"SP",
                "customer_city":"São Paulo",
                "customer_phone":"16997228598"
            },
            {
                "contract_date":"2025-06-10",
                "contract_amount":5000,
                "contract_rate":2.0,
                "customer_cpf":generate_random_cpf(),
                "customer_birth_date":"1976-10-26",
                "customer_country":"Brasil",
                "customer_state":"RJ",
                "customer_city":"Rio de Janeiro",
                "customer_phone":"16997228598"
            },
            {
                "contract_date":"2025-06-11",
                "contract_amount":8000,
                "contract_rate":2.5,
                "customer_cpf":generate_random_cpf(),
                "customer_birth_date":"1976-10-26",
                "customer_country":"Brasil",
                "customer_state":"AM",
                "customer_city":"Manaus",
                "customer_phone":"16997228598"
            }            
        ]
        for CONTRACT in self.contract_data_bulk:
            parcel_amount = math.trunc(((CONTRACT['contract_amount']*CONTRACT['contract_rate'])/self.max_parcels)*100)/100
            CONTRACT['parcels'] = []
            for I in range(self.max_parcels):
                CONTRACT['parcels'].append({
                        "parcel_number":I+1,"parcel_amount":parcel_amount,
                        "parcel_due_date":(dt.strptime(str(self.contract_data['contract_date']),"%Y-%m-%d").date() + relativedelta(months=I+1)).strftime('%Y-%m-%d')
                    }
                )

    def test_create_contract(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Contract.objects.count(),1)
        # imprime o nome da função atuaL test_create_contract
        print("test_create_contract: SUCCESS! Contract successfully created!")

    def test_create_contract_normalize_cpf(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(self.contract_data['customer_cpf'].replace('.','').replace('-',''),response.data['customer_cpf'])
        print("test_create_contract_normalize_cpf: SUCCESS! CPF normalized successfully!")

    def test_create_contract_invalid_cpf(self):
        url = reverse('create')
        self.contract_data['customer_cpf'] = '12345678901'
        response = self.client.post(url,self.contract_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        print("test_create_contract_invalid_cpf: SUCCESS! Invalid CPF detected!")

    def test_create_contract_normalize_uf(self):
        url = reverse('create')
        self.contract_data['customer_state'] = get_a_random_state_code().lower()
        response = self.client.post(url,self.contract_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(self.contract_data['customer_state'].upper(),response.data['customer_state'])
        print("test_create_contract_normalize_uf: SUCCESS! UF normalized successfully!")

    def test_create_contract_invalid_uf(self):
        url = reverse('create')
        self.contract_data['customer_state'] = 'ZZ'
        response = self.client.post(url,self.contract_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        print("test_create_contract_invalid_uf: SUCCESS! Invalid UF detected!")

    def test_create_contract_bulk(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Contract.objects.count(),4)
        print("test_create_contract_bulk: SUCCESS! Mass contracts created successfully!")

    def test_create_no_parcels(self):
        url = reverse('create')
        del self.contract_data['parcels']
        response = self.client.post(url,self.contract_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        print("test_create_no_parcels: SUCCESS! No parcels provided!")

    def test_create_invalid_parcel_amount(self):
        url = reverse('create')
        for parcel in self.contract_data['parcels']:
            parcel['parcel_amount'] -= 100
        response = self.client.post(url,self.contract_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        print("test_create_invalid_parcel_amount: SUCCESS! Invalid parcel amount detected!")

    def test_list_all(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('list_all')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),4)
        print("test_list_all: SUCCESS! All contracts listed successfully!")

    def test_list_filter_by_year(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('list') + "?contract_date=2024"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        print("test_list_filter_by_year: SUCCESS! Contracts filtered by year successfully!")

    def test_list_filter_by_year_month(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('list') + "?contract_date=2024-12"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        print("test_list_filter_by_year_month: SUCCESS! Contracts filtered by year and month successfully!")

    def test_list_filter_by_year_month_day(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('list') + "?contract_date=2025-06-09"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        print("test_list_filter_by_year_month_day: SUCCESS! Contracts filtered by year, month and day successfully!")
        
    def test_list_filter_by_cpf(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('list') + "?customer_cpf=" + self.contract_data_bulk[0]['customer_cpf']
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        print("test_list_filter_by_cpf: SUCCESS! Contracts filtered by CPF successfully!")

    def test_list_filter_by_state(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('list') + "?customer_state=" + self.contract_data_bulk[0]['customer_state']
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        print("test_list_filter_by_state: SUCCESS! Contracts filtered by state successfully!")
        
    def test_summary(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('summary') + "?customer_cpf=" + self.contract_data_bulk[0]['customer_cpf']
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIn('total_contracts_amount', response.data)
        self.assertIn('total_amount_to_receive', response.data)
        self.assertIn('total_number_of_contracts', response.data)
        self.assertIn('average_contract_rate', response.data)
        print("test_summary: SUCCESS! Contracts summary retrieved successfully!")

    def test_summary_no_contracts(self):
        url = reverse('summary') + "?customer_cpf=" + generate_random_cpf()
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_number_of_contracts'],0)
        print("test_summary_no_contracts: SUCCESS! No contracts found!")

    def test_summary_filter_by_cpf(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('summary') + "?customer_cpf=" + self.contract_data_bulk[0]['customer_cpf']
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_number_of_contracts'],1)
        print("test_summary_filter_by_cpf: SUCCESS! Contracts summary filtered by CPF successfully!")
        
    def test_summary_filter_by_invalid_cpf(self):
        url = reverse('summary') + "?customer_cpf=12345678901"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        print("test_summary_filter_by_invalid_cpf: SUCCESS! Invalid CPF detected!")

    def test_summary_filter_by_state(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('summary') + "?customer_state=" + self.contract_data_bulk[0]['customer_state']
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_number_of_contracts'],1)
        print("test_summary_filter_by_state: SUCCESS! Contracts summary filtered by state successfully!")
        
    def test_summary_filter_by_invalid_state(self):
        url = reverse('summary') + "?customer_state=ZZ"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        print("test_summary_filter_by_state_invalid: SUCCESS! Invalid state detected!")

    def test_summary_filter_by_year(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('summary') + "?contract_date=2024"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_number_of_contracts'],1)
        print("test_summary_filter_by_year: SUCCESS! Contracts summary filtered by year successfully!")

    def test_summary_filter_by_year_month(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('summary') + "?contract_date=2024-12"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_number_of_contracts'],1)
        print("test_summary_filter_by_year_month: SUCCESS! Contracts summary filtered by year and month successfully!")

    def test_summary_filter_by_year_month_day(self):
        url = reverse('create')
        response = self.client.post(url,self.contract_data_bulk,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        url = reverse('summary') + "?contract_date=2025-06-09"
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_number_of_contracts'],1)
        print("test_summary_filter_by_year_month_day: SUCCESS! Contracts summary filtered by year, month and day successfully!")
        