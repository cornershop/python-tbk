
import unittest

from tbk.oneclick import OneClick

from .utils import create_commerce


class TestOneClick(unittest.TestCase):
    def setUp(self):
        self.commerce_code = '597020000547'
        self.commerce = create_commerce(self.commerce_code)

    def test_init_inscription(self):
        oneclick = OneClick.init_for_commerce(self.commerce)

        response_url = "http://127.0.0.1:8000/sample/tbk_oneclick/OneClickFinishInscription"
        username = "usuario"
        email = "usuario@transbank.cl"

        inscription = oneclick.init_inscription(username, email, response_url)

        assert hasattr(inscription, 'token')
        assert hasattr(inscription, 'urlWebpay')
