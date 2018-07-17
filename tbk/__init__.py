
from .__about__ import __version__  # noqa

from .services import OneClickPaymentService, WebpayService, CommerceIntegrationService

from . import services  # noqa

INTEGRACION = 'INTEGRACION'
CERTIFICACION = 'CERTIFICACION'
PRODUCCION = 'PRODUCCION'


OneClick = OneClickPaymentService
WebpayNormal = WebpayService
DeferredCapture = CommerceIntegrationService
Nullify = CommerceIntegrationService
