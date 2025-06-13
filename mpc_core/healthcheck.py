import os
import time
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from datetime import datetime as dt

@api_view(['GET'])
def HealthCheck(request):
    ##──── Se existir um arquivo chamado "stop_hc" no diretório atual, o healthcheck retornará 404. 
    ##──── Para poder remover uma instância do load balancer em 15s sem envolver outras equipes 
    if os.path.isfile(os.path.join(os.path.dirname(__file__),"stop_hc")):
        return HttpResponse("health check stopped",status=status.HTTP_404_NOT_FOUND)
    ##──── Caso contrário, retorna 200.
    return HttpResponse("health check ok",status=status.HTTP_200_OK)

##──── Função para testar as dependencias do backend e retornar um teste rápido para uso interno 
@api_view(['GET'])
def HealthCheckTest(request):
    start_time = time.monotonic()
    response_data = { # simulando um teste de saúde do sistema
            "system_status": "ok",
            "database_conn": True,
            "database_conn_elapsed_time": '%.9f'%(time.monotonic()-start_time),
            "redis_session_server_conn": True,
            "redis_session_server_conn_elapsed_time": '%.9f'%(time.monotonic()-start_time),
            "authenticator_server_conn": True,
            "authenticator_server_elapsed_time": '%.9f'%(time.monotonic()-start_time),
            "other_dependencies": True,
            "other_dependencies_elapsed_time": '%.9f'%(time.monotonic()-start_time),
            # pelo gunicorn cada worker tem seu próprio APP_START_TIME
            "application_uptime": str(dt.now()-settings.APP_START_TIME), 
            "system_load": "normal",
            "system_memory_usage": "normal",
            "system_disk_space": "sufficient",
            "system_cpu_usage": "normal",
            "system_network_status": "connected",
            "system_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "system_version": "1.0.0",
            "system_environment": "production",
            "system_health_check": True,
            "system_health_check_elapsed_time": '%.9f'%(time.monotonic()-start_time),
            "system_security_status": "secure",
            "system_security_status_elapsed_time": '%.9f'%(time.monotonic()-start_time),
            "system_performance_metrics": {
                "cpu_usage": "low",
                "memory_usage": "low",
                "disk_usage": "normal",
                "network_latency": "low"
            },
            "total_elapsed_time": '%.9f'%(time.monotonic()-start_time)
        }
    return JsonResponse(response_data)
    