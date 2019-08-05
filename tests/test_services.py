import unittest

from tbk.commerce import Commerce
from tbk.services import OneClickPaymentService, WebpayService
from tbk.soap.requestor import SoapRequestor
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
            method_name="removeUser",
            input_name="oneClickRemoveUserInput",
            tbkUser=tbk_user,
            username=username,
        )


class WebpayServiceTest(ServiceTestCase):

    service_class = WebpayService
