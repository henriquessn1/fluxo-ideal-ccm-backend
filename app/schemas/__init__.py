from .client import ClientCreate, ClientUpdate, ClientResponse, ClientWithInstances
from .instance import InstanceCreate, InstanceUpdate, InstanceResponse
from .module import ModuleCreate, ModuleUpdate, ModuleResponse
from .installation import InstallationCreate, InstallationUpdate, InstallationResponse, InstallationWithDetails
from .endpoint import EndpointCreate, EndpointUpdate, EndpointResponse
from .threshold import ThresholdCreate, ThresholdUpdate, ThresholdResponse
from .monitoring_log import MonitoringLogCreate, MonitoringLogResponse, MonitoringLogWithDetails, MonitoringLogQuery

# Legacy schemas (will be removed/updated)
from .service import ServiceCreate, ServiceUpdate, ServiceResponse
from .health_check import HealthCheckResponse

__all__ = [
    # New schemas
    "ClientCreate",
    "ClientUpdate", 
    "ClientResponse",
    "ClientWithInstances",
    "InstanceCreate",
    "InstanceUpdate",
    "InstanceResponse",
    "ModuleCreate",
    "ModuleUpdate",
    "ModuleResponse",
    "InstallationCreate",
    "InstallationUpdate",
    "InstallationResponse",
    "InstallationWithDetails",
    "EndpointCreate",
    "EndpointUpdate",
    "EndpointResponse",
    "ThresholdCreate",
    "ThresholdUpdate",
    "ThresholdResponse",
    "MonitoringLogCreate",
    "MonitoringLogResponse",
    "MonitoringLogWithDetails",
    "MonitoringLogQuery",
    # Legacy schemas
    "ServiceCreate",
    "ServiceUpdate",
    "ServiceResponse",
    "HealthCheckResponse"
]