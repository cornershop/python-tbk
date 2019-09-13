import logging
from collections import namedtuple

from .soap import create_soap_requestor

StoreInput = namedtuple(
    "StoreInput", ["buy_order", "shares_number", "amount", "commerce_id"]
)


class TBKWebService(object):
    def __init__(self, commerce, soap_requestor=None, **client_kwargs):
        self.logger = logging.getLogger(
            "tbk.services.{}".format(self.__class__.__name__)
        )
        self.logger.info(
            "Initializing service for commerce %s in %s environment.",
            commerce.commerce_code,
            commerce.environment,
        )
        self.commerce = commerce
        self.soap_requestor = soap_requestor or create_soap_requestor(
            wsdl_url=self.get_wsdl_url_for_environment(commerce.environment),
            commerce=commerce,
            **client_kwargs
        )

    @classmethod
    def get_wsdl_url_for_environment(cls, environment):
        try:
            return getattr(cls, "WSDL_{}".format(environment))
        except AttributeError:
            raise ValueError("Invalid environment {}".format(environment))


class OneClickPaymentService(TBKWebService):

    WSDL_DEVELOPMENT = "https://webpay3gint.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl"
    WSDL_CERTIFICATION = "https://webpay3gint.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl"
    WSDL_PRODUCTION = "https://webpay3g.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl"

    def init_inscription(self, username, email, response_url):
        arguments = {"username": username, "email": email, "responseURL": response_url}
        one_click_inscription_input = self.soap_requestor.create_object(
            "oneClickInscriptionInput", **arguments
        )
        return self.soap_requestor.request(
            "initInscription", one_click_inscription_input
        )

    def finish_inscription(self, token):
        finish_inscription_input = self.soap_requestor.create_object(
            "oneClickFinishInscriptionInput", token=token
        )
        return self.soap_requestor.request(
            "finishInscription", finish_inscription_input
        )

    def authorize(self, buy_order, tbk_user, username, amount):
        arguments = {
            "buyOrder": buy_order,
            "tbkUser": tbk_user,
            "username": username,
            "amount": amount,
        }
        pay_input = self.soap_requestor.create_object("oneClickPayInput", **arguments)
        return self.soap_requestor.request("authorize", pay_input)

    def code_reverse_oneclick(self, buyorder):
        reverse_input = self.soap_requestor.create_object(
            "oneClickReverseInput", buyorder=buyorder
        )
        return self.soap_requestor.request("codeReverseOneClick", reverse_input)

    def remove_user(self, tbk_user, username):
        arguments = {"tbkUser": tbk_user, "username": username}
        one_click_remove_user_input = self.soap_requestor.create_object(
            "oneClickRemoveUserInput", **arguments
        )
        return self.soap_requestor.request("removeUser", one_click_remove_user_input)


class WebpayService(TBKWebService):

    WSDL_DEVELOPMENT = (
        "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl"
    )
    WSDL_CERTIFICATION = (
        "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl"
    )
    WSDL_PRODUCTION = (
        "https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl"
    )

    def init_transaction(
        self, amount, buy_order, return_url, final_url, session_id=None
    ):
        transaction_type = self.soap_requestor.get_enum_value(
            "wsTransactionType", "TR_NORMAL_WS"
        )
        arguments = {
            "wSTransactionType": transaction_type,
            "commerceId": self.commerce.commerce_code,
            "buyOrder": buy_order,
            "sessionId": session_id,
            "returnURL": return_url,
            "finalURL": final_url,
            "transactionDetails": [
                self.soap_requestor.create_object(
                    "wsTransactionDetail",
                    amount=amount,
                    commerceCode=self.commerce.commerce_code,
                    buyOrder=buy_order,
                )
            ],
        }
        init_transaction_input = self.soap_requestor.create_object(
            "wsInitTransactionInput", **arguments
        )
        return self.soap_requestor.request("initTransaction", init_transaction_input)

    def get_transaction_result(self, token):
        return self.soap_requestor.request("getTransactionResult", token)

    def acknowledge_transaction(self, token):
        return self.soap_requestor.request("acknowledgeTransaction", token)


class CommerceIntegrationService(TBKWebService):

    WSDL_DEVELOPMENT = "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl"
    WSDL_CERTIFICATION = "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl"
    WSDL_PRODUCTION = "https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl"

    def nullify(self, authorization_code, authorized_amount, buy_order, nullify_amount):
        arguments = {
            "authorizationCode": authorization_code,
            "authorizedAmount": authorized_amount,
            "buyOrder": buy_order,
            "commerceId": self.commerce.commerce_code,
            "nullifyAmount": nullify_amount,
        }
        nullification_input = self.soap_requestor.create_object(
            "nullificationInput", **arguments
        )
        return self.soap_requestor.request("nullify", nullification_input)

    def capture(self, authorization_code, capture_amount, buy_order):
        arguments = {
            "commerceId": self.commerce.commerce_code,
            "authorizationCode": authorization_code,
            "buyOrder": buy_order,
            "captureAmount": capture_amount,
        }
        capture_input = self.soap_requestor.create_object("captureInput", **arguments)
        return self.soap_requestor.request("capture", capture_input)


class CompleteWebpayService(TBKWebService):

    WSDL_DEVELOPMENT = "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCompleteWebpayService?wsdl"
    WSDL_CERTIFICATION = "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCompleteWebpayService?wsdl"
    WSDL_PRODUCTION = "https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSCompleteWebpayService?wsdl"

    def init_complete_transaction(
        self, amount, buy_order, card_expiration_date, cvv, card_number, session_id=None
    ):
        transaction_type = self.soap_requestor.get_enum_value(
            "wsCompleteTransactionType", "TR_COMPLETA_WS"
        )

        card_detail_arguments = {
            "cardExpirationDate": card_expiration_date,
            "cvv": cvv,
            "cardNumber": card_number,
        }
        card_detail = self.soap_requestor.create_object(
            "completeCardDetail", **card_detail_arguments
        )

        transaction_details_arguments = {
            "amount": amount,
            "buyOrder": buy_order,
            "commerceCode": self.commerce.commerce_code,
        }
        transaction_details = self.soap_requestor.create_object(
            "wsCompleteTransactionDetail", **transaction_details_arguments
        )

        transaction_input_arguments = {
            "transactionType": transaction_type,
            "sessionId": session_id,
            "cardDetail": card_detail,
            "transactionDetails": transaction_details,
        }

        transaction_input = self.soap_requestor.create_object(
            "wsCompleteInitTransactionInput", **transaction_input_arguments
        )

        return self.soap_requestor.request("initCompleteTransaction", transaction_input)

    def queryshare(self, token, buy_order, share_number):
        arguments = {"token": token, "buyOrder": buy_order, "shareNumber": share_number}
        queryshare_input = self.soap_requestor.create_object(
            "wsCompleteQueryShareInput", **arguments
        )

        return self.soap_requestor.request("queryShare", queryshare_input)

    def authorize(
        self, token, buy_order, grace_period, id_query_share, deferred_period_index
    ):
        query_share_input_arguments = {
            "idQueryShare": id_query_share,
            "deferredPeriodIndex": deferred_period_index,
        }
        query_share_input = self.soap_requestor.create_object(
            "wsCompleteQueryShareInput", **query_share_input_arguments
        )

        payment_type_input_arguments = {
            "buyOrder": buy_order,
            "commerceCode": self.commerce.commerce_code,
            "gracePeriod": grace_period,
            "queryShareInput": query_share_input,
        }
        payment_type_input = self.soap_requestor.create_object(
            "wsCompletePaymentTypeInput", **payment_type_input_arguments
        )

        authorize_arguments = {"token": token, "paymentTypeList": payment_type_input}
        authorize_input = self.soap_requestor.create_object(
            "authorize", **authorize_arguments
        )

        return self.soap_requestor.request("authorize", authorize_input)

    def acknowledge_transaction(self, token):
        return self.soap_requestor.request("acknowledgeTransaction", token)


class OneClickMulticodeService(TBKWebService):
    WSDL_DEVELOPMENT = "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSOneClickMulticodeService?wsdl"
    WSDL_CERTIFICATION = "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSOneClickMulticodeService?wsdl"
    WSDL_PRODUCTION = "https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSOneClickMulticodeService?wsdl"


    StoreInput = namedtuple(
        "StoreInput", ["commerce_id", "buy_order", "amount", "shares_number"]
    )

    def init_inscription(self, username, email, response_url):
        arguments = {"username": username, "email": email, "returnUrl": response_url}
        one_click_inscription_input = self.soap_requestor.create_object(
            "wsOneClickMulticodeInitInscriptionInput", **arguments
        )
        return self.soap_requestor.request(
            "initInscription", one_click_inscription_input
        )

    def finish_inscription(self, token):
        finish_inscription_input = self.soap_requestor.create_object(
            "wsOneClickMulticodeFinishInscriptionInput", token=token
        )
        return self.soap_requestor.request(
            "finishInscription", finish_inscription_input
        )

    def authorize(self, buy_order, tbk_user, username, store_inputs):

        input_args = {
            "username": username,
            "tbkUser": tbk_user,
            "buyOrder": buy_order,
            "storesInput": [
                {
                    "buyOrder": store_input.buy_order,
                    "sharesNumber": store_input.shares_number,
                    "amount": store_input.amount,
                    "commerceId": store_input.commerce_id,
                }
                for store_input in store_inputs
            ],
        }
        pay_input = self.soap_requestor.create_object(
            "wsOneClickMulticodePaymentInput", **input_args
        )
        return self.soap_requestor.request("authorize", pay_input)

    def capture(self, authorization_code, commerce_id, buy_order, capture_amount):

        input_args = {
            "commerceId": commerce_id,
            "buyOrder": buy_order,
            "authorizationCode": authorization_code,
            "captureAmount": capture_amount,
        }

        capture_input = self.soap_requestor.create_object(
            "wsOneClickMulticodeCaptureInput", **input_args
        )
        return self.soap_requestor.request("capture", capture_input)

    def reverse_nullification(self, buy_order, nullify_amount, commerce_id):
        reverse_input = self.soap_requestor.create_object(
            "wsOneClickMulticodeReverseNullificationInput",
            buyOrder=buy_order,
            commerceId=commerce_id,
            nullifyAmount=nullify_amount,
        )
        return self.soap_requestor.request("reverseNullification", reverse_input)

    def reverse(self, buy_order):
        reverse_input = self.soap_requestor.create_object(
            "wsOneClickMulticodeReverseInput", buyOrder=buy_order
        )
        return self.soap_requestor.request("reverse", reverse_input)

    def nullify(
        self,
        commerce_id,
        buy_order,
        authorization_code,
        authorized_amount,
        nullify_amount,
    ):
        nullify_input = self.soap_requestor.create_object(
            "wsOneClickMulticodeNullificationInput",
            commerceId=commerce_id,
            buyOrder=buy_order,
            authorizedAmount=authorized_amount,
            authorizationCode=authorization_code,
            nullifyAmount=nullify_amount,
        )
        return self.soap_requestor.request("nullify", nullify_input)

    def remove_user(self, tbk_user, username):
        arguments = {"tbkUser": tbk_user, "username": username}

        one_click_remove_user_input = self.soap_requestor.create_object(
            "wsOneClickMulticodeRemoveInscriptionInput", **arguments
        )
        return self.soap_requestor.request(
            "removeInscription", one_click_remove_user_input
        )
