# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .service import WebpayService


class WebpayNormal(WebpayService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'
    WSDL_CERTIFICATION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'

    def init_transaction(self, amount, buy_order, return_url, final_url, session_id=None):
        arguments = {
            'wSTransactionType': 'TR_NORMAL_WS',
            'commerceId': self.commerce.commerce_code,
            'buyOrder': buy_order,
            'sessionId': session_id,
            'returnURL': return_url,
            'finalURL': final_url,
            'transactionDetails': [
                (
                    'wsTransactionDetail',
                    {
                        'amount': amount,
                        'commerceCode': self.commerce.commerce_code,
                        'buyOrder': buy_order
                    }
                )
            ],
            'wPMDetail': ('wpmDetailInput', {})
        }
        init_transaction_input = self.soap_client.create_input('wsInitTransactionInput', arguments)
        return self.soap_client.request('initTransaction', init_transaction_input)

    def get_transaction_result(self, token):
        return self.soap_client.request('getTransactionResult', token)

    def acknowledge_transaction(self, token):
        return self.soap_client.request('acknowledgeTransaction', token)
