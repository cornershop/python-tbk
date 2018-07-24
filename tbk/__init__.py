
from .__about__ import __version__  # noqa

from . import commerce
from . import services

from .soap.exceptions import SoapServerException  # noqa


__all__ = ['services', 'INTEGRACION', 'CERTIFICACION', 'PRODUCCION']

INTEGRACION = 'INTEGRACION'
CERTIFICACION = 'CERTIFICACION'
PRODUCCION = 'PRODUCCION'


# Shortcuts
Commerce = commerce.Commerce
OneClickPaymentService = services.OneClickPaymentService
WebpayService = services.WebpayService
CommerceIntegrationService = services.CommerceIntegrationService

# Note: support legacy names for services, will be deprecated very soon
OneClick = OneClickPaymentService
WebpayNormal = WebpayService
DeferredCapture = CommerceIntegrationService
Nullify = CommerceIntegrationService
