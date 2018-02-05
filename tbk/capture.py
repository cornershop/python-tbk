# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .service import WebpayService


class DeferredCapture(WebpayService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'
    WSDL_CERTIFICACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'

    def capture(self, authorization_code, capture_amount, buy_order):
        arguments = {
            'commerceId': self.commerce.commerce_code,
            'authorizationCode': authorization_code,
            'buyOrder': buy_order,
            'captureAmount': capture_amount
        }
        capture_input = self.soap_client.create_input('captureInput', arguments)
        return self.soap_client.request('capture', capture_input)
