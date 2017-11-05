# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .service import WebpayService


class OneClick(WebpayService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl'
    WSDL_CERTIFICACION = 'https://webpay3gint.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl'

    def init_inscription(self, username, email, response_url):
        arguments = {
            'username': username,
            'email': email,
            'responseURL': response_url
        }
        one_click_inscription_input = self.soap_client.create_input('oneClickInscriptionInput', arguments)
        return self.soap_client.request('initInscription', one_click_inscription_input)

    def finish_inscription(self, token):
        arguments = {'token': token}
        one_click_finish_inscription_input = self.soap_client.create_input('oneClickFinishInscriptionInput', arguments)
        return self.soap_client.request('finishInscription', one_click_finish_inscription_input)

    def authorize(self, buy_order, tbk_user, username, amount):
        arguments = {
            'buyOrder': buy_order,
            'tbkUser': tbk_user,
            'username': username,
            'amount': amount
        }
        one_click_pay_input = self.soap_client.create_input('oneClickPayInput', arguments)
        return self.soap_client.request('authorize', one_click_pay_input)

    def code_reverse_oneclick(self, buyorder):
        arguments = {'buyorder': buyorder}
        one_click_reverse_input = self.soap_client.create_input('oneClickReverseInput', arguments)
        return self.soap_client.request('codeReverseOneClick', one_click_reverse_input)

    def remove_user(self, tbk_user, username):
        arguments = {
            'tbkUser': tbk_user,
            'username': username
        }
        one_click_remove_user_input = self.soap_client.create_input('oneClickRemoveUserInput', arguments)
        return self.soap_client.request('oneClickRemoveUser', one_click_remove_user_input)
