from . import commerce
from . import services
from . import environments

from .soap.exceptions import SoapServerException  # noqa

__all__ = ["services", "environments"]

__version__ = "0.2.2"

# services shortcuts
Commerce = commerce.Commerce
OneClickPaymentService = services.OneClickPaymentService
WebpayService = services.WebpayService
CommerceIntegrationService = services.CommerceIntegrationService

# environments shortcuts
DEVELOPMENT = environments.DEVELOPMENT
CERTIFICATION = environments.CERTIFICATION
PRODUCTION = environments.PRODUCTION


# Note: support legacy names for services, will be deprecated very soon
OneClick = OneClickPaymentService
WebpayNormal = WebpayService
DeferredCapture = CommerceIntegrationService
Nullify = CommerceIntegrationService

# NOTE: Legacy environment names, will be deprecated very soon
INTEGRACION = DEVELOPMENT
CERTIFICACION = CERTIFICATION
PRODUCCION = PRODUCTION
