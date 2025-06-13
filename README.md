# Case Guardian MPC (Management of Personal Credit)

## Instalação
Clone o repositório em um diretório de sua preferência:
```
git clone https://github.com/rabuchaim/guardian_mpc.git
```
Entre no diretório do código recém clonado:
```
cd guardian_mpc
```
Crie um ambiente virtual do Python3:
```
python3 -m venv python-venv
```
> Se ocorrer algum erro na criação do ambiente virtual você deve instalar o pacote python3-venv do seu sistema operacional com `apt install python3-venv` ou `yum install python3-venv`

Ative o ambiente virtual:
```
source python-venv/bin/activate
```
Instale as bibliotecas necessárias:
```
pip install -r requirements.txt
```
Execute o makemigrations e depois o migrate:
```
./manage.py makemigrations mpc_contracts
./manage.py migrate
```
Execute os testes da aplicação para verificar se está tudo instalado corretamente:
```
./manage.py test
```
Saída esperada do comando `./manage.py test`:
```bash
$ ./manage.py test
Found 23 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
test_create_contract: SUCCESS! Contract successfully created!
.test_create_contract_bulk: SUCCESS! Mass contracts created successfully!
.test_create_contract_invalid_cpf: SUCCESS! Invalid CPF detected!
.test_create_contract_invalid_uf: SUCCESS! Invalid UF detected!
.test_create_contract_normalize_cpf: SUCCESS! CPF normalized successfully!
.test_create_contract_normalize_uf: SUCCESS! UF normalized successfully!
.test_create_invalid_parcel_amount: SUCCESS! Invalid parcel amount detected!
.test_create_no_parcels: SUCCESS! No parcels provided!
.test_list_all: SUCCESS! All contracts listed successfully!
.test_list_filter_by_cpf: SUCCESS! Contracts filtered by CPF successfully!
.test_list_filter_by_state: SUCCESS! Contracts filtered by state successfully!
.test_list_filter_by_year: SUCCESS! Contracts filtered by year successfully!
.test_list_filter_by_year_month: SUCCESS! Contracts filtered by year and month successfully!
.test_list_filter_by_year_month_day: SUCCESS! Contracts filtered by year, month and day successfully!
.test_summary: SUCCESS! Contracts summary retrieved successfully!
.test_summary_filter_by_cpf: SUCCESS! Contracts summary filtered by CPF successfully!
.test_summary_filter_by_invalid_cpf: SUCCESS! Invalid CPF detected!
.test_summary_filter_by_state_invalid: SUCCESS! Invalid state detected!
.test_summary_filter_by_state: SUCCESS! Contracts summary filtered by state successfully!
.test_summary_filter_by_year: SUCCESS! Contracts summary filtered by year successfully!
.test_summary_filter_by_year_month: SUCCESS! Contracts summary filtered by year and month successfully!
.test_summary_filter_by_year_month_day: SUCCESS! Contracts summary filtered by year, month and day successfully!
.test_summary_no_contracts: SUCCESS! No contracts found!
.
----------------------------------------------------------------------
Ran 23 tests in 0.165s

OK
Destroying test database for alias 'default'...
```

## Endpoints

### **Criação de Contrato**: `POST` `/contracts/create/`

Cria um novo contrato. Aceita envio em massa.

### **Listagem de todos os contratos**: `GET` `/contracts/list/all`


### **Listagem de contratos com filtro**: `GET` `/contracts/list/`


### **Resumo consolidado dos contratos (com filtro)**: `GET` `/contracts/summary/`


### **HealthCheck para o load balancer**: `GET` `/hc/`

Se existir um arquivo chamado `stop_hc` no diretório `mpc_core`, o healthcheck retornará `404` para poder remover a instância de um load balancer em menos de 15 segundos sem envolver outras equipes.

```bash
$ touch mpc_core/stop_hc
$ curl -L -v "http://127.0.0.1:8000/hc/"
health check stopped
```

Se o arquivo `stop_hc` não existir, retorna `200`

```bash
$ curl -L -v "http://127.0.0.1:8000/hc/"
health check ok
```

### **Teste interno da saúde da instância/aplicação**: `GET` `/hc/test`

Função para testar as dependencias do backend e retornar um teste rápido para uso interno. *Os dados abaixo são uma simulação*
```bash
curl -L "http://127.0.0.1:8000/hc/test/" | jq
```
```json
{
  "system_status": "ok",
  "database_conn": true,
  "database_conn_elapsed_time": "0.000000738",
  "redis_session_server_conn": true,
  "redis_session_server_conn_elapsed_time": "0.000004626",
  "authenticator_server_conn": true,
  "authenticator_server_elapsed_time": "0.000005504",
  "other_dependencies": true,
  "other_dependencies_elapsed_time": "0.000006077",
  "application_uptime": "0:25:37.312304",
  "system_load": "normal",
  "system_memory_usage": "normal",
  "system_disk_space": "sufficient",
  "system_cpu_usage": "normal",
  "system_network_status": "connected",
  "system_time": "2025-06-13 01:54:33",
  "system_version": "1.0.0",
  "system_environment": "production",
  "system_health_check": true,
  "system_health_check_elapsed_time": "0.000027730",
  "system_security_status": "secure",
  "system_security_status_elapsed_time": "0.000028412",
  "system_performance_metrics": {
    "cpu_usage": "low",
    "memory_usage": "low",
    "disk_usage": "normal",
    "network_latency": "low"
  },
  "total_elapsed_time": "0.000029253"
}
```

## Validações

São feitas validações no backend (mesmo que já exista no frontend) para caso ocorra alguma falha no frontend ou até mesmo um acesso burlando o frontend, o banco de dados não será onerado com consultas inválidas. As validações ocorrem na criação e nas consultas com filtro.

#### **- Documento CPF do tomador do empréstimo**

Só é aceito CPF válido. Se o CPF for informado com pontos ou traços, ocorre a normalização (remoção dos pontos ou traços) antes de salvar no banco. A mesma coisa ocorre durante as consultas com filtro.

#### **- Localidade Estado do tomador do empréstimo**

Só aceita siglas válidas de estados brasileiros. Se informado em letras minúsculas, ocorre a normalização para maiúsculas.

Exemplo:

```bash
$ curl -L -v "http://127.0.0.1:8000/contracts/summary/?customer_state=XX"

< HTTP/1.1 400 Bad Request
["Invalid customer_state code: XX. Must be one of 'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'"]
```

#### **- Soma das parcelas**

A soma do valor de todas as parcelas tem que ser igual ou superior ao valor do contrato multiplicado pela taxa de contrato. 

Exemplo: 
```bash
$ curl -v -X POST http://127.0.0.1:8000/contracts/create/ -H "Content-Type: application/json" -d '{"contract_date":"2023-01-15","contract_amount
":20000,"contract_rate":2.3,"customer_cpf":"24926156857","customer_birth_date":"1990-01-01","customer_country":"Brasil","customer_state":"SP","customer_city":"São Paulo","customer_phone":"
16997228598","parcels":[{"parcel_due_date":"2025-08-01","parcel_amount":11500},{"parcel_due_date":"2025-09-01","parcel_amount":11500},{"parcel_due_date":"2025-10-01","parcel_amount":11500}
,{"parcel_due_date":"2025-11-01","parcel_amount":10500}]}'

< HTTP/1.1 400 Bad Request
{"error":"[ErrorDetail(string='The total of parcel amounts must be greater than or equal to the contract amount multiplied by contract rate. In this case, greater than or equal to 46000.0', code='invalid')]"}
```

#### **- Total de parcelas**

Tem que existir ao menos 1 parcela

#### **- Valor das parcelas**

As parcelas podem ter valores diferentes, porém tem que ser maior do que ZERO.

#### **- Data das parcelas**

A data das parcelas tem que ser posterior à data do contrato

#### **- Valor do contrato**

O valor do contrato tem que ser maior que ZERO.

#### **- Taxa de contrato**

A taxa de contrato tem que ser maior ou igual a 1.

