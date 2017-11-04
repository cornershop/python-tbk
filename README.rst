=========================================
Unofficial Webpay Web Services Python SDK
=========================================

🇬🇧

Installation
============

Just run::

	$ python setup.py install


Usage
=====

As simple as call (snakecased) webpay api methods::

	>>> from tbk import WebpayNormal, Commerce, INTEGRACION
	>>> commerce = commerce = Commerce(commerce_code, key_data, cert_data, tbk_cert_data, INTEGRACION)
	>>> webpay_normal = WebpayNormal.init_for_commerce(commerce)
	>>> transaction = webpay_normal.init_transaction(amount, buy_order, return_url, final_url)
	>>> print(transaction.token)
	e87df74f7af4dcfdc1d17521b07413ff9a004a7b423dc47ad09f6a8166a73842


Conventions
===========

This library use a snake cased naming convention for webservices and params for a more pythonic implementation. Every camelcased name in the webpay API was transformed to snakecase::

	initTransaction(amount, buyOrder, returnURL, finalURL, sessionId)

became::

	init_transaction(amount, buy_order, return_url, final_url, session_id)


Documentation
=============

You can refer to http://www.transbankdevelopers.cl/?m=api for official API documentation. This library documentation is on the way.


🇪🇸

Intalación
==========

Ejecuta ::

	$ python setup.py install


Uso
===

Tan simple como llamar los métodos del API de Webpay (pero snakecased)::

	>>> from tbk import WebpayNormal, Commerce, INTEGRACION
	>>> commerce = commerce = Commerce(commerce_code, key_data, cert_data, tbk_cert_data, INTEGRACION)
	>>> webpay_normal = WebpayNormal.init_for_commerce(commerce)
	>>> transaction = webpay_normal.init_transaction(amount, buy_order, return_url, final_url)
	>>> print(transaction.token)
	e87df74f7af4dcfdc1d17521b07413ff9a004a7b423dc47ad09f6a8166a73842


Convenciones
============

La librería usa una convención de nombres snakecased para ser más pythonica. Cada nombre camelcased en el API de Webpay se transformó a snakecased::

	initTransaction(amount, buyOrder, returnURL, finalURL, sessionId)

se traduce en::

	init_transaction(amount, buy_order, return_url, final_url, session_id)


Documentación
=============

La documentación oficial se encuentra disponible en http://www.transbankdevelopers.cl/?m=api. La documentación de esta librería está en desarrollo.


