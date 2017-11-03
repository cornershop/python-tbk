Unofficial Webpay Web Services Python SDK
=========================================

Installation
------------

	$ python setup.py install


Usage
-----

	>>> from tbk import WebpayNormal, Commerce, INTEGRACION
	>>> commerce = commerce = Commerce(commerce_code, key_data, cert_data, tbk_cert_data, INTEGRACION)
	>>> webpay_normal = WebpayNormal.init_for_commerce(commerce)
	>>> transaction = webpay_normal.init_transaction(amount, buy_order, return_url, final_url)
	>>> print transaction.token
