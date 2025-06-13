from django.urls import path, include
from .healthcheck import HealthCheck, HealthCheckTest

urlpatterns = [
    # path("admin/", admin.site.urls),
    path('hc/',HealthCheck),
    path('hc/test/',HealthCheckTest),
    path('contracts/',include('mpc_contracts.urls'))
]
