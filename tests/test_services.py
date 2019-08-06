import unittest

from tbk import Commerce
from tbk.services import OneClickPaymentService, WebpayService, OneClickMulticodeService
from tbk.soap import SoapRequestor
from .utils import mock


class ServiceTestCase(unittest.TestCase):

    service_class = None

    def setUp(self):
        self.soap_requestor = mock.MagicMock(spec=SoapRequestor)
        self.commerce = mock.MagicMock(
            spec=Commerce,
            commerce_code=mock.MagicMock(spec=str),
            environment=mock.MagicMock(spec=str),
        )
        self.service = self.service_class(self.commerce, self.soap_requestor)

    def assert_result_and_request_with_input(
        self, result, method_name, input_name, **input_kwargs
    ):
        self.assertEqual(self.soap_requestor.request.return_value, result)
        self.soap_requestor.create_object.assert_called_once_with(
            input_name, **input_kwargs
        )
        self.soap_requestor.request.assert_called_once_with(
            method_name, self.soap_requestor.create_object.return_value
        )


class OneClickPaymentServiceTest(ServiceTestCase):

    service_class = OneClickPaymentService

    def test_init_inscription(self):
        username = mock.MagicMock(spec=str)
        email = mock.MagicMock(spec=str)
        response_url = mock.MagicMock(spec=str)

        result = self.service.init_inscription(
            username=username, email=email, response_url=response_url
        )

        self.assert_result_and_request_with_input(
            result=result,
            method_name="initInscription",
            input_name="oneClickInscriptionInput",
            email=email,
            responseURL=response_url,
            username=username,
        )

    def test_finish_inscription(self):
        token = mock.MagicMock(spec=str)

        result = self.service.finish_inscription(token)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="finishInscription",
            input_name="oneClickFinishInscriptionInput",
            token=token,
        )

    def test_authorize(self):
        buy_order = mock.MagicMock(spec=str)
        tbk_user = mock.MagicMock(spec=str)
        username = mock.MagicMock(spec=str)
        amount = mock.MagicMock(spec=int)

        result = self.service.authorize(buy_order, tbk_user, username, amount)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="authorize",
            input_name="oneClickPayInput",
            buyOrder=buy_order,
            tbkUser=tbk_user,
            username=username,
            amount=amount,
        )

    def test_code_reverse_oneclick(self):
        buyorder = mock.MagicMock(spec=str)

        result = self.service.code_reverse_oneclick(buyorder)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="codeReverseOneClick",
            input_name="oneClickReverseInput",
            buyorder=buyorder,
        )

    def test_remove_user(self):
        tbk_user = mock.MagicMock(spec=str)
        username = mock.MagicMock(spec=str)

        result = self.service.remove_user(tbk_user, username)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="oneClickRemoveUser",
            input_name="oneClickRemoveUserInput",
            tbkUser=tbk_user,
            username=username,
        )


class OneClickMallServiceTest(ServiceTestCase):

    service_class = OneClickMulticodeService

    def test_init_inscription(self):
        username = mock.MagicMock(spec=str)
        email = mock.MagicMock(spec=str)
        response_url = mock.MagicMock(spec=str)

        result = self.service.init_inscription(
            username=username, email=email, response_url=response_url
        )

        self.assert_result_and_request_with_input(
            result=result,
            method_name="initInscription",
            input_name="wsOneClickMulticodeInitInscriptionInput",
            email=email,
            returnUrl=response_url,
            username=username,
        )

    def test_finish_inscription(self):
        token = mock.MagicMock(spec=str)

        result = self.service.finish_inscription(token)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="finishInscription",
            input_name="wsOneClickMulticodeFinishInscriptionInput",
            token=token,
        )

    def test_authorize(self):
        buy_order = mock.MagicMock(spec=str)
        tbk_user = mock.MagicMock(spec=str)
        username = mock.MagicMock(spec=str)
        amount = mock.MagicMock(spec=int)
        commerce = mock.MagicMock(spec=str)

        stores_inputs = [
            {
                "buy_order": buy_order,
                "shares": 1,
                "amount": amount,
                "commerce_id": commerce,
            }
        ]

        result = self.service.authorize(buy_order, tbk_user, username, stores_inputs)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="authorize",
            input_name="wsOneClickMulticodePaymentInput",
            buyOrder=buy_order,
            tbkUser=tbk_user,
            username=username,
            storesInput=[
                {
                    "buyOrder": buy_order,
                    "sharesNumber": 1,
                    "amount": amount,
                    "commerceId": commerce,
                }
            ],
        )

    def test_authorize_multiple(self):
        buy_order = mock.MagicMock(spec=str)
        tbk_user = mock.MagicMock(spec=str)
        username = mock.MagicMock(spec=str)
        amount = mock.MagicMock(spec=int)
        commerce = mock.MagicMock(spec=str)
        buy_order_2 = mock.MagicMock(spec=str)
        amount_2 = mock.MagicMock(spec=int)
        commerce_2 = mock.MagicMock(spec=str)

        stores_inputs = [
            {
                "buy_order": buy_order,
                "shares": 1,
                "amount": amount,
                "commerce_id": commerce,
            },
            {
                "buy_order": buy_order_2,
                "shares": 3,
                "amount": amount_2,
                "commerce_id": commerce_2,
            },
        ]

        result = self.service.authorize(buy_order, tbk_user, username, stores_inputs)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="authorize",
            input_name="wsOneClickMulticodePaymentInput",
            buyOrder=buy_order,
            tbkUser=tbk_user,
            username=username,
            storesInput=[
                {
                    "buyOrder": buy_order,
                    "sharesNumber": 1,
                    "amount": amount,
                    "commerceId": commerce,
                },
                {
                    "buyOrder": buy_order_2,
                    "sharesNumber": 3,
                    "amount": amount_2,
                    "commerceId": commerce_2,
                },
            ],
        )

    def test_reverse(self):
        buyorder = mock.MagicMock(spec=str)

        result = self.service.reverse(buyorder)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="reverse",
            input_name="wsOneClickMulticodeReverseInput",
            buyOrder=buyorder,
        )

    def test_nullify(self):
        buy_order = mock.MagicMock(spec=str)
        authorization_code = mock.MagicMock(spec=str)
        authorized_amount = mock.MagicMock(spec=int)
        commerce_id = mock.MagicMock(spec=str)
        nullify_amount = authorized_amount / 2

        result = self.service.nullify(
            commerce_id=commerce_id,
            buy_order=buy_order,
            authorized_amount=authorized_amount,
            authorization_code=authorization_code,
            nullify_amount=nullify_amount,
        )

        self.assert_result_and_request_with_input(
            result=result,
            method_name="nullify",
            input_name="wsOneClickMulticodeNullificationInput",
            commerceId=commerce_id,
            buyOrder=buy_order,
            authorizedAmount=authorized_amount,
            authorizationCode=authorization_code,
            nullifyAmount=nullify_amount,
        )

    def test_capture(self):
        buy_order = mock.MagicMock(spec=str)
        authorization_code = mock.MagicMock(spec=str)
        capture_amount = mock.MagicMock(spec=int)
        commerce_id = mock.MagicMock(spec=str)

        result = self.service.capture(
            commerce_id=commerce_id,
            buy_order=buy_order,
            capture_amount=capture_amount,
            authorization_code=authorization_code,
        )

        self.assert_result_and_request_with_input(
            result=result,
            method_name="capture",
            input_name="wsOneClickMulticodeCaptureInput",
            commerceId=commerce_id,
            buyOrder=buy_order,
            captureAmount=capture_amount,
            authorizationCode=authorization_code,
        )

    def test_remove_user(self):
        tbk_user = mock.MagicMock(spec=str)
        username = mock.MagicMock(spec=str)

        result = self.service.remove_user(tbk_user, username)

        self.assert_result_and_request_with_input(
            result=result,
            method_name="removeInscription",
            input_name="wsOneClickMulticodeRemoveInscriptionInput",
            tbkUser=tbk_user,
            username=username,
        )

    def test_reverse_nullification(self):
        buy_order = mock.MagicMock(spec=str)
        nullify_amount = mock.MagicMock(spec=int)
        commerce_id = mock.MagicMock(spec=str)

        result = self.service.reverse_nullification(
            buy_order=buy_order, commerce_id=commerce_id, nullify_amount=nullify_amount
        )

        self.assert_result_and_request_with_input(
            result=result,
            method_name="reverseNullification",
            input_name="wsOneClickMulticodeReverseNullificationInput",
            commerceId=commerce_id,
            nullifyAmount=nullify_amount,
            buyOrder=buy_order,
        )


class WebpayServiceTest(ServiceTestCase):

    service_class = WebpayService
