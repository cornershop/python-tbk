
import unittest
import os

from tbk import WebpayNormal

from .utils import create_commerce

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


class TestWebpayNormal(unittest.TestCase):
    def setUp(self):
        self.commerce_code = '597020000541'
        self.commerce = create_commerce(self.commerce_code)

    def test_normal(self):
        webpay_normal = WebpayNormal.init_for_commerce(self.commerce)

        final_url = "http://127.0.0.1:8000/sample/tbk_normal/end"
        return_url = "http://127.0.0.1:8000/sample/tbk_normal/result"
        amount = '1500'
        buy_order = '1234'

        transaction = webpay_normal.init_transaction(amount, buy_order, return_url, final_url)

        assert hasattr(transaction, 'token')
        assert hasattr(transaction, 'urlWebpay')
