
import os
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from tbk import WebpayNormal
from tbk.suds_client import SudsSoapClient

from .utils import create_commerce, DATA_DIR

WSDL_URL = "file:///{}".format(os.path.join(DATA_DIR, "WsWebpayService.wsdl"))


class TestWebpayNormal(unittest.TestCase):
    def setUp(self):
        self.commerce_code = '597020000541'
        self.commerce = create_commerce(self.commerce_code)
        self.soap_client = SudsSoapClient(
            WSDL_URL,
            self.commerce.key_data,
            self.commerce.cert_data,
            self.commerce.tbk_cert_data
        )

    @mock.patch("tbk.service.SoapClient.request")
    @mock.patch("tbk.service.SoapClient.create_input")
    def test_init_transaction(self, create_input, request):
        webpay_normal = WebpayNormal(self.commerce, self.soap_client)

        amount = mock.Mock()
        buy_order = mock.Mock()
        return_url = mock.Mock()
        final_url = mock.Mock()
        session_id = mock.Mock()

        result = webpay_normal.init_transaction(
            amount, buy_order, return_url, final_url, session_id
        )

        self.assertEqual(result, request.return_value)
        request.assert_called_once_with('initTransaction', create_input.return_value)

    def test_init_transaction_input(self):
        amount = mock.Mock()
        buy_order = mock.Mock()
        return_url = mock.Mock()
        final_url = mock.Mock()
        session_id = mock.Mock()
        expected = _suds_init_transaction(
            self.soap_client.client, self.commerce.commerce_code, amount, buy_order, return_url, final_url, session_id
        )
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

        result = self.soap_client.create_input('wsInitTransactionInput', arguments)

        self.assertEqual(_suds2dict(expected), _suds2dict(result))

    @mock.patch('tbk.service.SoapClient.request')
    def test_get_transaction_result(self, request):
        webpay_normal = WebpayNormal(self.commerce, self.soap_client)
        token = mock.Mock(spec=str)

        transaction = webpay_normal.get_transaction_result(token)

        self.assertEqual(request.return_value, transaction)
        request.assert_called_once_with('getTransactionResult', token)

    @mock.patch('tbk.service.SoapClient.request')
    def test_acknowledge_transaction(self, request):
        webpay_normal = WebpayNormal(self.commerce, self.soap_client)
        token = mock.Mock(spec=str)

        transaction = webpay_normal.get_transaction_result(token)

        self.assertEqual(request.return_value, transaction)
        request.assert_called_once_with('getTransactionResult', token)


def _suds_init_transaction(client, commerce_code, amount, buy_order, return_url, final_url, session_id):
    init_transaction = client.factory.create('wsInitTransactionInput')
    init_transaction.wSTransactionType = client.factory.create('wsTransactionType').TR_NORMAL_WS
    init_transaction.commerceId = commerce_code
    init_transaction.buyOrder = buy_order
    init_transaction.sessionId = session_id
    init_transaction.returnURL = return_url
    init_transaction.finalURL = final_url
    transaction_detail = client.factory.create('wsTransactionDetail')
    transaction_detail.amount = amount
    transaction_detail.commerceCode = commerce_code
    transaction_detail.buyOrder = buy_order
    init_transaction.transactionDetails.append(transaction_detail)
    init_transaction.wPMDetail = client.factory.create('wpmDetailInput')
    return init_transaction


def _suds2dict(suds_instance):
    from suds.sudsobject import asdict
    out = {'__class__': suds_instance.__class__.__name__}
    for k, v in asdict(suds_instance).items():
        if hasattr(v, '__keylist__'):
            out[k] = _suds2dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(_suds2dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out
