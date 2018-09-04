======================================
Unofficial TBK Web Services Python SDK
======================================

🇬🇧

Testing cards
=============

Credit

+----------------+------------------+------------------+
| Marca          | VISA             | MASTERCARD       |
+================+==================+==================+
| No de Tarjeta  | 4051885600446623 | 5186059559590568 |
+----------------+------------------+------------------+
| Año Expiración | Cualquiera       | Cualquiera       |
+----------------+------------------+------------------+
| CVV            | 123              | 123              |
+----------------+------------------+------------------+
| Resultado      | APROBADO         | RECHAZADO        |
+----------------+------------------+------------------+

Debit

+----------+------------------+------------------+
|          | APRUEBA          | RECHAZA          |
+==========+==================+==================+
| TARJETA  | 4051885600446620 | 5186059559590560 |
+----------+------------------+------------------+
| RUT      | 11.111.111-1     | 11.111.111-1     |
+----------+------------------+------------------+
| PASSWORD | 123              | 123              |
+----------+------------------+------------------+


Installation
============

Just run::

    $ pipenv install python-tbk

or::

    $ pip install python-tbk


Usage
=====

As simple as call (snakecased) webpay api methods::

    >>> from tbk.services import WebpayService
    >>> from tbk.commerce import Commerce
    >>> from tbk import INTEGRACION
    >>> commerce = Commerce(commerce_code, key_data, cert_data, tbk_cert_data, INTEGRACION)
    >>> webpay = WebpayService(commerce)
    >>> transaction = webpay.init_transaction(amount, buy_order, return_url, final_url)
    >>> print(transaction['token'])
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


Loggers
=======

There are two levels of loggers::

    tbk.services
    tbk.soap

Specific service logger are defined by class name::

    tbk.services.WebpayService


Bugs?
=====

Issues are welcome at https://github.com/cornershop/python-tbk/issues


🇪🇸

Instalación
===========

Ejecuta::

    $ pipenv install python-tbk

ó::

    $ pip install python-tbk


Uso
===

Tan simple como llamar los métodos del API de Webpay (pero snakecased)::

    >>> from tbk.services import WebpayService
    >>> from tbk.commerce import Commerce
    >>> from tbk import INTEGRACION
    >>> commerce = Commerce(commerce_code, key_data, cert_data, tbk_cert_data, INTEGRACION)
    >>> webpay = WebpayService(commerce)
    >>> transaction = webpay.init_transaction(amount, buy_order, return_url, final_url)
    >>> print(transaction['token'])
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


Loggers
=======

Se encuentran definidos dos niveles de logger::

    tbk.services
    tbk.soap

El logger específico de un servicio está definido por su nombre de clase::

    tbk.services.WebpayService

