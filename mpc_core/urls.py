from django.urls import path, include
from django.conf import settings
from .healthcheck import HealthCheck, HealthCheckTest

urlpatterns = [
    # path("admin/", admin.site.urls),
    path(settings.HC_PREFIX+'hc/',HealthCheck),
    path(settings.HC_PREFIX+'hc/test/',HealthCheckTest),
    path(settings.API_PREFIX+'contracts/',include('mpc_contracts.urls'))
]
