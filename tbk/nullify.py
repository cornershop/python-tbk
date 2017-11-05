# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .service import WebpayService


class Nullify(WebpayService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'
    WSDL_CERTIFICACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'

    def nullify(self, authorization_code, authorized_amount, buy_order, nullify_amount):
        arguments = {
            'authorizationCode': authorization_code,
            'authorizedAmount': authorized_amount,
            'buyOrder': buy_order,
            'commerceId': self.commerce.commerce_code,
            'nullifyAmount': nullify_amount
        }
        nullification_input = self.soap_client.create_input('nullificationInput', arguments)
        return self.soap_client.request('nullify', nullification_input)
